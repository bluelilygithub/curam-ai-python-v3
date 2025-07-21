"""
Australian Property Intelligence API V3
Professional Flask application with PostgreSQL + User Switching
UPDATED: Clean architecture with user switching functionality,
live logging, dynamic questions, and delete functionality.
"""

import os
import sys
import logging
import time
import queue
import json
import threading
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

# --- Global Queue for Live Log Streamer ---
log_queue = queue.Queue()

# --- Custom Logging Handler for Live Stream ---
class QueueHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
                "level": record.levelname,
                "message": self.format(record),
                "name": record.name 
            }
            log_queue.put(json.dumps(log_entry))
        except Exception:
            self.handleError(record)

# --- Application-wide Logging Setup ---
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 
logging.getLogger().addHandler(QueueHandler()) 

logger.info("✅ Live log stream handler initialized and attached to root logger.")


# --- Import professional services and Config ---
from config import Config
from services import LLMService, PropertyAnalysisService 
from enhanced_database import PropertyDatabase 
from services.web_search_service import WebSearchService 
from utils import HealthChecker

app = Flask(__name__)

CORS(app, origins=Config.CORS_ORIGINS)

# --- Backend Services Initialization Function ---
def initialize_services():
    services = {}
    
    Config.log_config_status()
    Config.validate_config()

    try:
        services['database'] = PropertyDatabase()
        logger.info("✅ PostgreSQL database service initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        services['database'] = None
    
    if Config.CLAUDE_ENABLED or Config.GEMINI_ENABLED:
        try:
            services['llm'] = LLMService()
            logger.info("✅ LLM service initialized")
        except Exception as e:
            logger.error(f"❌ LLM service initialization failed: {e}")
            services['llm'] = None
    else:
        logger.warning("⚠️ LLM Service skipped: No Claude or Gemini API keys configured.")
        services['llm'] = None

    try:
        from services.rss_service import RSSService 
        services['rss'] = RSSService()
        logger.info("✅ RSS service initialized")
    except Exception as e:
        logger.error(f"❌ RSS service initialization failed: {e}")
        services['rss'] = None

    if Config.GOOGLE_CSE_ENABLED:
        try:
            services['web_search'] = WebSearchService()
            logger.info("✅ Web Search service initialized.")
            if not services['web_search'].is_available: 
                logger.warning("⚠️ Web Search service is not fully available due to missing configuration (API key/CX).")
        except Exception as e:
            logger.error(f"❌ Web Search service initialization failed: {e}")
            services['web_search'] = None
    else:
        logger.warning("⚠️ Web Search service skipped: Google CSE API keys not configured.")
        services['web_search'] = None
    
    if services['llm']:
        try:
            # Pass LLMService, RSSService, and WebSearchService instances to PropertyAnalysisService
            services['property'] = PropertyAnalysisService(services['llm'], services['rss'], services['web_search']) 
            logger.info("✅ Property analysis service initialized")
        except Exception as e:
            logger.error(f"❌ Property service initialization failed: {e}")
            services['property'] = None
    else:
        logger.warning("⚠️ Property Analysis service skipped: LLM service not available.")
        services['property'] = None
    
    try:
        services['health'] = HealthChecker(services)
        logger.info("✅ Health checker initialized")
    except Exception as e:
        logger.error(f"❌ Health checker initialization failed: {e}")
        services['health'] = None
    
    available_services = [name for name, service in services.items() if service is not None]
    logger.info(f"🚀 All core services initialized: {', '.join(available_services)}")
    
    return services

# --- Initialize Services on app startup ---
services = initialize_services()

# --- LLM Performance Analysis Utility Function ---
def analyze_llm_performance(recent_queries):
    """Analyzes LLM performance from recent database queries to populate dashboard charts."""
    try:
        if not recent_queries:
            return {
                'response_times': [],
                'provider_performance': {
                    'claude': {'avg_response_time': 0, 'success_rate': 100, 'total_queries': 0}, 
                    'gemini': {'avg_response_time': 0, 'success_rate': 100, 'total_queries': 0}
                },
                'location_breakdown': {},
                'success_rates': {'overall': 100, 'claude': 100, 'gemini': 100}
            }
        
        response_times = []
        for query in recent_queries[-10:]: 
            response_times.append({
                'query_id': query.get('id', 0),
                'processing_time': query.get('processing_time', 0),
                'timestamp': query.get('created_at', '')
            })
        
        claude_queries = [q for q in recent_queries if q.get('llm_provider') == 'claude']
        gemini_queries = [q for q in recent_queries if q.get('llm_provider') == 'gemini']
        
        provider_performance = {
            'claude': {
                'avg_response_time': round(sum(q['processing_time'] for q in claude_queries if 'processing_time' in q) / len(claude_queries), 2) if claude_queries and any('processing_time' in q for q in claude_queries) else 0,
                'success_rate': round(sum(1 for q in claude_queries if q.get('success', True)) / len(claude_queries) * 100, 1) if claude_queries else 100,
                'total_queries': len(claude_queries)
            },
            'gemini': {
                'avg_response_time': round(sum(q['processing_time'] for q in gemini_queries if 'processing_time' in q) / len(gemini_queries), 2) if gemini_queries and any('processing_time' in q for q in gemini_queries) else 0,
                'success_rate': round(sum(1 for q in gemini_queries if q.get('success', True)) / len(gemini_queries) * 100, 1) if gemini_queries else 100,
                'total_queries': len(gemini_queries)
            }
        }
        
        location_breakdown = {}
        for query in recent_queries:
            location = query.get('location_detected', 'National')
            location_breakdown[location] = location_breakdown.get(location, 0) + 1
        
        successful_queries = sum(1 for q in recent_queries if q.get('success', True))
        overall_success_rate = (successful_queries / len(recent_queries) * 100) if recent_queries else 100
        
        return {
            'response_times': response_times,
            'provider_performance': provider_performance,
            'location_breakdown': location_breakdown,
            'success_rates': {
                'overall': round(overall_success_rate, 1),
                'claude': provider_performance['claude']['success_rate'],
                'gemini': provider_performance['gemini']['success_rate']
            }
        }
        
    except Exception as e:
        logger.error(f"LLM performance analysis failed: {e}")
        return {
            'error': str(e),
            'response_times': [], 
            'provider_performance': {
                'claude': {'avg_response_time': 0, 'success_rate': 100, 'total_queries': 0}, 
                'gemini': {'avg_response_time': 0, 'success_rate': 100, 'total_queries': 0}
            },
            'location_breakdown': {'National': 1},
            'success_rates': {'overall': 100, 'claude': 100, 'gemini': 100}
        }

# --- User-Specific Default Questions Function ---
def get_user_specific_default_questions(user_id: str) -> list:
    """Returns user-specific default questions based on user profile."""
    user_defaults = {
        'sarah_buyer': [
            "Best suburbs under $600k for first home buyers in Brisbane",
            "Units near train stations with good transport links",
            "First home buyer grants and assistance programs", 
            "Safest affordable suburbs for young professionals",
            "What areas have the best schools and family amenities?"
        ],
        'michael_investor': [
            "High rental yield suburbs in Brisbane",
            "Investment property hotspots 2025",
            "Logan vs Ipswich for property investment",
            "Brisbane outer suburbs with growth potential",
            "What are the best strategies for property portfolio growth?"
        ]
    }
    return user_defaults.get(user_id, Config.DEFAULT_EXAMPLE_QUESTIONS)

# --- Activity Log Management Functions ---
def clear_activity_log():
    """
    Clears the activity log queue for a fresh start with new questions.
    This ensures users only see logs relevant to their current analysis.
    """
    global log_queue
    cleared_count = 0
    try:
        while not log_queue.empty():
            log_queue.get_nowait()
            cleared_count += 1
    except queue.Empty:
        pass
    
    clear_signal = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "level": "SYSTEM",
        "message": "🔄 Activity log cleared for new question",
        "name": "system",
        "action": "clear_log"  # Special action for frontend
    }
    log_queue.put(json.dumps(clear_signal))
    
    if cleared_count > 0:
        logger.debug(f"Cleared {cleared_count} old log entries from activity log")

# ================================
# MAIN API ROUTES
# ================================

@app.route('/')
def api_info():
    """Provides general information about the Australian Property Intelligence API V3."""
    return jsonify({
        'name': 'Australian Property Intelligence API',
        'version': '3.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'description': 'Enterprise multi-LLM Australian property analysis with PostgreSQL and user switching',
        'features': [
            'PostgreSQL Database with SQLAlchemy ORM',
            'User Switching and Personalized Analytics',
            'Multi-LLM Integration (Claude + Gemini)',
            'Location Intelligence Tracking',
            'Real Australian Property RSS Feeds',
            'Enhanced Performance Monitoring',
            'Professional Error Handling',
            'Live Log Streaming (SSE)',
            'Web Search Integration for Factual Lookups',
            'LLM Token Usage Tracking & Limits' # NEW FEATURE
        ],
        'services': services['health'].get_service_status() if services['health'] else {},
        'api_endpoints': { # List all available API endpoints for clarity
            'info': 'GET /',
            'health_check': 'GET /health',
            'live_logs': 'GET /stream_logs',
            'get_users': 'GET /api/users',
            'get_user_stats': 'GET /api/users/{user_id}/stats',
            'get_user_history': 'GET /api/users/{user_id}/history',
            'get_questions': 'GET /api/property/questions',
            'analyze_property': 'POST /api/property/analyze',
            'get_property_history': 'GET /api/property/history',
            'delete_property_query': 'DELETE /api/property/history/{query_id}',
            'get_property_stats': 'GET /api/property/stats'
        }
    })

@app.route('/health')
def health_check_endpoint():
    """Provides a comprehensive health check for all integrated backend services."""
    if not services['health']:
        logger.error("Health checker service is not available during health check request.")
        return jsonify({
            'status': 'error',
            'error': 'Health checker not available',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    return jsonify(services['health'].get_comprehensive_health())

# ================================
# LIVE LOG STREAMING (SSE) ENDPOINT
# ================================

@app.route('/stream_logs')
def stream_logs():
    """
    Server-Sent Events (SSE) endpoint to stream real-time log messages from the backend
    to connected frontend clients. This provides live updates for the activity log.
    """
    def generate():
        last_activity_time = time.time()
        while True:
            try:
                log_message = log_queue.get(timeout=0.5) 
                yield f"data: {log_message}\n\n" 
                last_activity_time = time.time() 
            except queue.Empty:
                if time.time() - last_activity_time > 15: 
                    yield ":keep-alive\n\n" 
                    last_activity_time = time.time() 
            except Exception as e:
                logger.error(f"Error in log stream generator: {e}")
                yield f"data: {json.dumps({'level': 'ERROR', 'message': f'Server stream error in SSE: {e}'})}\n\n"
                time.sleep(1) 
            
            time.sleep(0.01) 

    response = Response(stream_with_context(generate()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache" 
    response.headers["X-Accel-Buffering"] = "no" 
    response.headers["Connection"] = "keep-alive" 
    return response

# ================================
# USER SWITCHING API ROUTES
# ================================

@app.route('/api/users', methods=['GET'])
def get_demo_users():
    """Retrieves a list of available demo users for the frontend's user switching functionality."""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database service not available.'
        }), 500
    
    try:
        users = services['database'].get_demo_users()
        
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to retrieve demo users: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<user_id>/stats', methods=['GET'])
def get_user_statistics(user_id: str):
    """
    Retrieves comprehensive usage statistics for a specific user ID,
    including total tokens used and the session limit.
    """
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database service not available.'
        }), 500
    
    try:
        stats_data = services['database'].get_user_stats(user_id)
        
        if not stats_data: 
            logger.warning(f"Stats for user '{user_id}' not found or database error. Returning 404.")
            return jsonify({
                'success': False,
                'error': f"User '{user_id}' not found or no stats available."
            }), 404 
            
        # Add the global session token limit from Config to the stats data
        stats_data['stats']['max_session_tokens'] = Config.MAX_TOKENS_PER_SESSION 

        return jsonify({
            'success': True,
            'data': stats_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to retrieve user statistics for {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<user_id>/history', methods=['GET'])
def get_user_history(user_id: str):
    """Retrieves the query history for a specific user ID, with optional limit."""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database service not available.'
        }), 500
    
    try:
        limit = request.args.get('limit', 20, type=int)
        
        if not (1 <= limit <= 100): 
            logger.warning(f"Invalid history limit {limit} requested for user {user_id}. Defaulting to 20.")
            limit = 20
        
        history = services['database'].get_query_history(limit=limit, user_id=user_id)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'user_id': user_id,
            'limit': limit,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to retrieve user history for {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# PROPERTY ANALYSIS ROUTES
# ================================

@app.route('/api/property/analyze', methods=['POST'])
async def analyze_property_question():
    """
    Analyzes a user's property question with token usage tracking and session limits.
    """
    user_id = 'anonymous' 
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body must be JSON.'
            }), 400
        
        question = data.get('question', '').strip()
        user_id = data.get('user_id', 'anonymous')
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required.'
            }), 400
        
        if not services['property'] or not services['database']:
            return jsonify({
                'success': False,
                'error': 'Required services (Property Analysis or Database) not available.'
            }), 500

        # --- NEW: TOKEN USAGE LIMIT CHECK (PER SESSION) ---
        user_stats_before_query = services['database'].get_user_stats(user_id)
        current_session_tokens = user_stats_before_query.get('stats', {}).get('total_tokens_used', 0)
        
        if current_session_tokens >= Config.MAX_TOKENS_PER_SESSION:
            logger.warning(f"❌ User '{user_id}' reached session token limit ({current_session_tokens}/{Config.MAX_TOKENS_PER_SESSION}).")
            return jsonify({
                'success': False,
                'error': f"You have reached your session's token limit ({Config.MAX_TOKENS_PER_SESSION} tokens). Please start a new session or contact support.",
                'current_session_tokens': current_session_tokens,
                'max_session_tokens': Config.MAX_TOKENS_PER_SESSION
            }), 429 
        
        logger.info(f"🔍 DEBUG: About to clear activity log for user '{user_id}'")
        
        try:
            clear_activity_log()
            logger.info(f"✅ DEBUG: Activity log cleared successfully for user '{user_id}'")
        except Exception as e:
            logger.error(f"❌ DEBUG: Failed to clear activity log: {e}")
        
        if services.get('web_search'):
            logger.info(f"🌐 DEBUG: Web search service available: {services['web_search'].is_available}")
        else:
            logger.info("🌐 DEBUG: Web search service NOT available")
        
        logger.info(f"🔍 Processing property question for user '{user_id}': '{question[:70]}{'...' if len(question) > 70 else ''}'")
        start_time = time.time()
        
        # Call property analysis service; it now returns 'total_tokens_used'
        result = await services['property'].analyze_property_question(question)
        processing_time = time.time() - start_time
        
        # --- NEW: CAPTURE TOTAL TOKENS USED FROM RESULT ---
        total_tokens_for_this_query = result.get('total_tokens_used', 0)
        logger.info(f"📊 Total tokens for this query: {total_tokens_for_this_query}")

        location_detected = detect_location_from_question(question)
        llm_provider = determine_llm_provider(result)
        
        query_id = None
        if services['database'] and result['success']:
            try:
                query_id = services['database'].store_query(
                    question=question,
                    answer=result['final_answer'],
                    question_type=result.get('question_type', 'custom'),
                    processing_time=processing_time,
                    success=result['success'],
                    location_detected=location_detected,
                    llm_provider=llm_provider,
                    confidence_score=result.get('confidence', 0.85),
                    user_id=user_id,
                    total_tokens_used=total_tokens_for_this_query # NEW: Pass token count to store_query
                )
                logger.info(f"💾 Query stored successfully with ID: {query_id} for user: '{user_id}'. Tokens: {total_tokens_for_this_query}")

                # After storing, re-fetch user stats to get updated session token count
                updated_user_stats = services['database'].get_user_stats(user_id)
                updated_session_total_tokens = updated_user_stats.get('stats', {}).get('total_tokens_used', 0)

                # --- NEW: PUSH TOKEN USAGE TO SSE FOR REAL-TIME DISPLAY ---
                token_update_signal = {
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "level": "INFO",
                    "message": "📊 Token Usage Update",
                    "name": "system",
                    "action": "token_update", # Special action for frontend
                    "current_query_tokens": total_tokens_for_this_query,
                    "session_total_tokens": updated_session_total_tokens,
                    "max_session_tokens": Config.MAX_TOKENS_PER_SESSION,
                    "user_id": user_id
                }
                log_queue.put(json.dumps(token_update_signal))
                logger.info(f"📊 SSE: Sent token update for user {user_id}. Query: {total_tokens_for_this_query}, Session: {updated_session_total_tokens}")

            except Exception as e:
                logger.error(f"❌ Failed to store query or update token stats for user '{user_id}': {e}")
        
        sources_data = result.get('sources', {})
        logger.info(f"🔍 DEBUG: Building response with sources: {sources_data}")
        
        response = {
            'success': result['success'],
            'question': question,
            'answer': result['final_answer'],
            'processing_time': round(processing_time, 2),
            'query_id': query_id,
            'user_id': user_id,
            'sources': sources_data,
            'total_tokens_used': total_tokens_for_this_query, # NEW: Include token count in API response for consistency
            'debug_info': { 
                'web_search_available': services.get('web_search') is not None,
                'web_search_configured': services.get('web_search').is_available if services.get('web_search') else False,
                'result_keys': list(result.keys()),
                'sources_found': bool(sources_data)
            },
            'metadata': {
                'location_detected': location_detected,
                'llm_provider': llm_provider,
                'confidence': result.get('confidence', 0.85),
                'sources_used': {
                    'rss_count': len(sources_data.get('rss_sources', [])),
                    'search_count': len(sources_data.get('search_sources', [])),
                    'total_sources': sources_data.get('total_sources', 0)
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Analysis completed in {processing_time:.2f}s for user '{user_id}'.")
        logger.info(f"🔍 DEBUG: Final response sources: {response['sources']}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Property analysis pipeline failed for user '{user_id}': {e}")
        return jsonify({
            'success': False,
            'error': f"Failed to analyze question: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/property/questions', methods=['GET'])
def get_property_questions():
    """
    Provides personalized question suggestions to the frontend.
    Each user gets their own recent questions and user-specific defaults.
    """
    try:
        user_id = request.args.get('user_id', 'anonymous')
        questions = []
        
        logger.info(f"🔍 Getting personalized questions for user '{user_id}'")
        
        if services['database']:
            try:
                # 1. Get recent queries for THIS specific user (up to 5)
                recent_user_queries = services['database'].get_query_history(limit=5, user_id=user_id)
                for query_item in recent_user_queries:
                    questions.append({
                        'question': query_item['question'],
                        'type': 'recent_user', 
                        'user_specific': True,
                        'query_id': query_item['id'],
                        'count': 1
                    })
                logger.info(f"✅ Added {len(recent_user_queries)} recent queries for user '{user_id}'.")

                # 2. If user has few recent questions, get their own popular questions
                if len(questions) < 3:
                    user_popular_queries = services['database'].get_popular_questions(limit=3, user_id=user_id)
                    for item in user_popular_queries:
                        if not any(q['question'] == item['question'] for q in questions):
                            questions.append({
                                'question': item['question'],
                                'type': 'popular_user', 
                                'user_specific': True,
                                'query_id': item['id'],
                                'count': item['count']
                            })
                    logger.info(f"✅ Added {len(user_popular_queries)} popular queries for user '{user_id}'.")

            except Exception as e:
                logger.error(f"❌ Failed to retrieve dynamic questions from database: {e}")
        
        # 3. If user has NO personal questions, add user-specific defaults
        if not questions:
            default_questions = get_user_specific_default_questions(user_id)
            for question_text in default_questions:
                questions.append({
                    'question': question_text,
                    'type': 'example', 
                    'user_specific': True, 
                    'query_id': None,
                    'count': 0
                })
            logger.info(f"✅ Added {len(default_questions)} user-specific default questions for '{user_id}'.")
        
        return jsonify({
            'success': True,
            'questions': questions,
            'user_id': user_id,
            'total_count': len(questions),
            'personalization': 'user_specific', 
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get personalized questions for '{user_id}': {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'user_id': user_id
        }), 500

@app.route('/api/property/history', methods=['GET'])
def get_property_history():
    """Retrieves the full query history, optionally filtered by user ID and with a limit."""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database service not available.'
        }), 500
    
    try:
        limit = request.args.get('limit', 50, type=int)
        user_id = request.args.get('user_id')  

        if not (1 <= limit <= 1000): 
            logger.warning(f"Invalid history limit {limit} requested. Defaulting to 50.")
            limit = 50
        
        history = services['database'].get_query_history(limit=limit, user_id=user_id)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'user_id': user_id,
            'limit': limit,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to retrieve property history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/history/<int:query_id>', methods=['DELETE'])
def delete_query_by_id(query_id: int):
    """Deletes a specific query from the database history by its ID."""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database service not available.'
        }), 500
    
    try:
        success = services['database'].delete_query(query_id)
        
        if success:
            logger.info(f"🗑️ Query with ID {query_id} deleted successfully.")
            return jsonify({
                'success': True,
                'message': f"Query {query_id} deleted."
            }), 200 
        else:
            logger.warning(f"⚠️ Query with ID {query_id} not found or could not be deleted.")
            return jsonify({
                'success': False,
                'error': f"Query with ID {query_id} not found or could not be deleted."
            }), 404 
    except Exception as e:
        logger.error(f"❌ Error deleting query {query_id}: {e}")
        return jsonify({
            'success': False,
            'error': f"Server error while deleting query: {str(e)}"
        }), 500 

@app.route('/api/property/stats', methods=['GET'])
def get_property_stats():
    """Retrieves comprehensive system statistics, including LLM performance and database insights."""
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'version': '3.0.0',
                'python_version': sys.version.split()[0],
                'database_type': 'PostgreSQL + SQLAlchemy'
            }
        }
        
        if services['database']:
            try:
                db_stats = services['database'].get_database_stats()
                stats['database'] = db_stats
                
                recent_queries = services['database'].get_query_history(30) 
                
                llm_performance = analyze_llm_performance(recent_queries)
                stats['llm_performance'] = llm_performance
                
            except Exception as e:
                logger.error(f"Failed to retrieve database or LLM performance stats: {e}")
                stats['database'] = {'error': str(e)}
                stats['llm_performance'] = {'error': str(e)}
        else:
            stats['database'] = {'status': 'not_available'}
            stats['llm_performance'] = {'status': 'not_available'}
        
        if services['llm']:
            try:
                llm_health = services['llm'].get_health_status()
                stats['llm_providers'] = llm_health
            except Exception as e:
                logger.error(f"Failed to retrieve LLM provider health: {e}")
                stats['llm_providers'] = {'error': str(e)}
        
        if services['rss']:
            try:
                rss_health = services['rss'].get_health_status()
                stats['rss_status'] = rss_health
            except Exception as e:
                logger.error(f"Failed to retrieve RSS service status: {e}")
                stats['rss_status'] = {'error': str(e)}
        
        if services['web_search']:
            try:
                web_search_health = services['web_search'].get_health_status()
                stats['web_search_status'] = web_search_health
            except Exception as e:
                logger.error(f"Failed to retrieve Web Search service status: {e}")
                stats['web_search_status'] = {'error': str(e)}
        else:
            stats['web_search_status'] = {'status': 'not_available', 'details': 'Service not initialized'}
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get property statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# ACTIVITY LOG MANAGEMENT ENDPOINTS
# ================================

@app.route('/api/logs/clear', methods=['POST'])
def clear_activity_log_endpoint():
    """
    Manual endpoint to clear the activity log.
    Can be called by frontend before starting new questions.
    """
    try:
        clear_activity_log()
        return jsonify({
            'success': True,
            'message': 'Activity log cleared successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to clear activity log: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/debug/queries')
def debug_queries():
    """Temporary endpoint to see what's actually stored in the database by user."""
    if not services['database']:
        return {"error": "Database not available"}
    
    try:
        all_queries = services['database'].get_query_history(limit=50, user_id=None)
        
        user_breakdown = {}
        for query in all_queries:
            user = query.get('user_id', 'unknown')
            if user not in user_breakdown:
                user_breakdown[user] = []
            user_breakdown[user].append({
                'id': query['id'],
                'question': query['question'][:50] + '...',
                'created_at': query['created_at'],
                'llm_provider': query.get('llm_provider', 'unknown'),
                'total_tokens_used': query.get('total_tokens_used', 0) # Include token usage in debug
            })
        
        return {
            'total_queries': len(all_queries),
            'by_user': user_breakdown,
            'user_count': len(user_breakdown),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# ================================
# UTILITY FUNCTIONS
# ================================

def detect_location_from_question(question: str) -> str:
    """
    Detects a specific Australian city or 'National' scope based on keywords in the question.
    """
    if not question:
        return 'National'
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['brisbane', 'queensland', 'qld', 'gold coast', 'sunshine coast']):
        return 'Brisbane'
    elif any(word in question_lower for word in ['sydney', 'nsw', 'new south wales']):
        return 'Sydney'
    elif any(word in question_lower for word in ['melbourne', 'victoria', 'vic']):
        return 'Melbourne'
    elif any(word in question_lower for word in ['perth', 'western australia', 'wa']):
        return 'Perth'
    elif any(word in question_lower for word in ['adelaide', 'south australia', 'sa']):
        return 'Adelaide'
    elif any(word in question_lower for word in ['darwin', 'northern territory', 'nt']):
        return 'Darwin'
    else:
        return 'National'

def determine_llm_provider(result: dict) -> str:
    """
    Determines which LLM provider was used with improved error handling.
    """
    if not result or not isinstance(result, dict):
        return 'unknown'
    
    if 'llm_provider' in result:
        return result['llm_provider']
    
    if result.get('claude_result', {}).get('success', False):
        return 'claude'
    elif result.get('gemini_result', {}).get('success', False):
        return 'gemini'
    else:
        return 'unknown'

# ================================
# GLOBAL ERROR HANDLERS
# ================================

@app.errorhandler(400)
def bad_request_error_handler(error):
    """Handles HTTP 400 Bad Request errors."""
    return jsonify({
        'success': False,
        'error': 'Bad Request: The server could not understand the request due to invalid syntax.',
        'details': str(error),
        'timestamp': datetime.now().isoformat()
    }), 400

@app.errorhandler(404)
def not_found_error_handler(error):
    """Handles HTTP 404 Not Found errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found. Please check the URL.',
        'available_endpoints': [ 
            'GET /',
            'GET /health',
            'GET /stream_logs',
            'GET /api/users',
            'GET /api/users/{user_id}/stats',
            'GET /api/users/{user_id}/history',
            'GET /api/property/questions',
            'POST /api/property/analyze',
            'GET /api/property/history',
            'DELETE /api/property/history/{query_id}',
            'GET /api/property/stats',
            'GET /debug/queries'  
        ],
        'details': str(error),
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_server_error_handler(error):
    """Handles HTTP 500 Internal Server Errors."""
    logger.error(f"An unhandled internal server error occurred: {error}", exc_info=True) 
    return jsonify({
        'success': False,
        'error': 'Internal server error. An unexpected condition was encountered.',
        'details': 'Please try again later. If the problem persists, contact support.',
        'timestamp': datetime.now().isoformat()
    }), 500


@app.route('/debug/google-cse')
def debug_google_cse():
    """Debug Google CSE configuration"""
    api_key = os.getenv('Google Search_API_KEY')
    cx = os.getenv('Google Search_CX')
    
    return jsonify({
        'api_key_exists': bool(api_key),
        'api_key_starts_with': api_key[:10] if api_key else None,
        'cx_exists': bool(cx),
        'cx_value': cx,
        'google_cse_enabled': Config.GOOGLE_CSE_ENABLED,
        'web_search_service_exists': services.get('web_search') is not None,
        'web_search_available': services.get('web_search').is_available if services.get('web_search') else False,
        'environment_vars_found': {
            'GOOGLE_CSE_API_KEY': 'present' if api_key else 'missing',
            'GOOGLE_CSE_CX': 'present' if cx else 'missing'
        }
    })


# ================================
# APPLICATION ENTRY POINT
# ================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Australian Property Intelligence API V3.0")
    logger.info(f"📡 Port: {port}")
    logger.info(f"🔧 Debug Mode: {debug_mode}")
    logger.info(f"🗄️ Database: PostgreSQL + SQLAlchemy")
    logger.info(f"👥 User Switching: Enabled")
    
    if debug_mode:
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        pass