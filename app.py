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
# This queue is used by the custom logging handler to push log records
# which are then streamed to the frontend via Server-Sent Events (SSE).
log_queue = queue.Queue()

# --- Custom Logging Handler for Live Stream ---
class QueueHandler(logging.Handler):
    """
    A custom logging handler that puts log records into a global queue.
    These records can then be picked up by an SSE endpoint to stream to the frontend.
    """
    def emit(self, record):
        try:
            # Format the log record into a dictionary for JSON serialization
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
                "level": record.levelname,
                "message": self.format(record),
                "name": record.name # Name of the logger (e.g., __main__, services.llm_service)
            }
            # Put the JSON string into the thread-safe queue
            log_queue.put(json.dumps(log_entry))
        except Exception:
            # Handle errors that occur within the logger itself to prevent infinite loops
            self.handleError(record)

# --- Application-wide Logging Setup ---
# Configure basic logging to console (for local dev/Railway logs)
# AND add the custom QueueHandler to the root logger.
logging.basicConfig(level=logging.INFO) # Set default logging level to INFO
logger = logging.getLogger(__name__) # Get a logger instance for this module (app.py)
logging.getLogger().addHandler(QueueHandler()) # Attach the custom handler to the root logger

# Inform that the live log stream handler is ready
logger.info("✅ Live log stream handler initialized and attached to root logger.")


# --- Import professional services and Config (ensure these modules are correctly structured) ---
# These imports should be placed after basic logging setup but before Flask app initialization
# to ensure 'logger' and 'Config' are available when services are initialized.
from config import Config
from services import LLMService, PropertyAnalysisService
from enhanced_database import PropertyDatabase # Using enhanced_database.py
from services.web_search_service import WebSearchService # NEW: Import WebSearchService
from utils import HealthChecker
# Note: services.rss_service.RSSService is imported directly in initialize_services()

# --- Flask Application Instance Initialization ---
app = Flask(__name__)

# --- Configure Cross-Origin Resource Sharing (CORS) ---
# This allows your frontend (e.g., curam-ai.com.au) to make requests to this backend API.
CORS(app, origins=Config.CORS_ORIGINS)

# --- Backend Services Initialization Function ---
def initialize_services():
    """Initializes all custom backend services (Database, LLM, RSS, PropertyAnalysis, WebSearch, HealthChecker)
    with proper error handling and logging their status.
    """
    services = {}
    
    # Log the configured status from config.py
    Config.log_config_status()
    
    # NEW: Validate Config attributes directly
    Config.validate_config()

    # Initialize Database Service (using PostgreSQL with SQLAlchemy)
    try:
        services['database'] = PropertyDatabase()
        logger.info("✅ PostgreSQL database service initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        services['database'] = None
    
    # Initialize LLM Service (integrates Claude and Gemini)
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

    # Initialize RSS Service (for Australian Property Data)
    try:
        from services.rss_service import RSSService # Imported here to avoid circular dependencies if RSSService imports app
        services['rss'] = RSSService()
        logger.info("✅ RSS service initialized")
    except Exception as e:
        logger.error(f"❌ RSS service initialization failed: {e}")
        services['rss'] = None

    # Initialize Web Search Service
    if Config.GOOGLE_CSE_ENABLED:
        try:
            services['web_search'] = WebSearchService()
            logger.info("✅ Web Search service initialized.")
            if not services['web_search'].is_available: # Check availability after init for more granular logging
                logger.warning("⚠️ Web Search service is not fully available due to missing configuration (API key/CX).")
        except Exception as e:
            logger.error(f"❌ Web Search service initialization failed: {e}")
            services['web_search'] = None
    else:
        logger.warning("⚠️ Web Search service skipped: Google CSE API keys not configured.")
        services['web_search'] = None
    
    # Initialize Property Analysis Service (orchestrates LLM, RSS, and now Web Search)
    # This service depends on the LLM service being successfully initialized.
    if services['llm']:
        try:
            services['property'] = PropertyAnalysisService(services['llm'], services['rss'], services['web_search']) # Pass web_search_service
            logger.info("✅ Property analysis service initialized")
        except Exception as e:
            logger.error(f"❌ Property service initialization failed: {e}")
            services['property'] = None
    else:
        logger.warning("⚠️ Property Analysis service skipped: LLM service not available.")
        services['property'] = None
    
    # Initialize Health Checker Service (monitors the status of all other services)
    try:
        services['health'] = HealthChecker(services)
        logger.info("✅ Health checker initialized")
    except Exception as e:
        logger.error(f"❌ Health checker initialization failed: {e}")
        services['health'] = None
    
    # Log summary of all successfully initialized services
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
        
        # Extract response times for the line chart (last 10 queries)
        response_times = []
        for query in recent_queries[-10:]: # Limit to last 10 for dashboard display
            response_times.append({
                'query_id': query.get('id', 0),
                'processing_time': query.get('processing_time', 0),
                'timestamp': query.get('created_at', '')
            })
        
        # Analyze performance per LLM provider (Claude vs. Gemini)
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
        
        # Location breakdown by detected location
        location_breakdown = {}
        for query in recent_queries:
            location = query.get('location_detected', 'National')
            location_breakdown[location] = location_breakdown.get(location, 0) + 1
        
        # Calculate overall success rates
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
            'response_times': [], # Return empty lists/default values on error
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

# ================================
# MAIN API ROUTES
# These are the primary endpoints for the frontend application.
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
            'Web Search Integration for Factual Lookups' # Added this feature
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
    Uses a comment-only line (':keep-alive\\n\\n') for keep-alive messages to prevent
    connection timeouts from intermediate proxies/load balancers.
    """
    def generate():
        last_activity_time = time.time()
        while True:
            try:
                # Attempt to get a log message from the queue within a short timeout.
                # A timeout prevents the generator from blocking indefinitely if no new logs arrive.
                log_message = log_queue.get(timeout=0.5) # Poll queue every 0.5 seconds
                yield f"data: {log_message}\n\n" # Send the actual log message as SSE data
                last_activity_time = time.time() # Reset activity timer
            except queue.Empty:
                # If the queue is empty (no new logs), send a keep-alive comment.
                # This signals to proxies/load balancers that the connection is still active.
                if time.time() - last_activity_time > 15: # Send keep-alive every 15 seconds
                    yield ":keep-alive\n\n" # A comment line is usually ignored by SSE clients but keeps connection alive
                    last_activity_time = time.time() # Reset activity timer for keep-alives
            except Exception as e:
                # Log any errors that occur within this generator itself
                logger.error(f"Error in log stream generator: {e}")
                # Optionally, also send an error message to the client through the stream
                yield f"data: {json.dumps({'level': 'ERROR', 'message': f'Server stream error in SSE: {e}'})}\n\n"
                time.sleep(1) # Pause briefly after an error before trying again
            
            # A very small delay to prevent busy-waiting and high CPU usage,
            # ensuring other Flask requests can be processed.
            time.sleep(0.01) # Yield CPU for 10 milliseconds


    # Return the Flask Response object with the correct SSE mimetype and headers.
    response = Response(stream_with_context(generate()), mimetype="text/event-stream")
    # Add crucial headers for SSE to prevent caching and buffering by proxies.
    response.headers["Cache-Control"] = "no-cache" # Prevent caching of the stream
    response.headers["X-Accel-Buffering"] = "no" # Specific for Nginx-like proxies; tells it not to buffer
    response.headers["Connection"] = "keep-alive" # Ensure the connection stays open
    return response

# ================================
# USER SWITCHING API ROUTES
# These endpoints manage demo user data and associated statistics/history.
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
    """Retrieves comprehensive usage statistics for a specific user ID."""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database service not available.'
        }), 500
    
    try:
        stats = services['database'].get_user_stats(user_id)
        
        if not stats: # Check if get_user_stats explicitly returned None (though it should return a dict now)
            logger.warning(f"Stats for user '{user_id}' not found or database error. Returning 404.")
            return jsonify({
                'success': False,
                'error': f"User '{user_id}' not found or no stats available."
            }), 404 # 404 Not Found if user stats don't exist
            
        return jsonify({
            'success': True,
            'data': stats,
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
        
        # Validate and constrain the limit parameter
        if not (1 <= limit <= 100): # Allow between 1 and 100 queries
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
# These endpoints handle the core property analysis functionality.
# ================================

@app.route('/api/property/analyze', methods=['POST'])
async def analyze_property_question(): # Changed to async
    """
    Analyzes a user's property question using LLMs and RSS data,
    and stores the analysis result in the database.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body must be JSON.'
            }), 400
        
        question = data.get('question', '').strip()
        user_id = data.get('user_id', 'anonymous') # Track user ID for analysis
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required.'
            }), 400
        
        if not services['property']:
            return jsonify({
                'success': False,
                'error': 'Property analysis service not available.'
            }), 500
        
        logger.info(f"🔍 Processing property question for user '{user_id}': '{question[:70]}{'...' if len(question) > 70 else ''}'")
        start_time = time.time()
        
        # Use professional property analysis service
        result = await services['property'].analyze_property_question(question) # Await the async call
        processing_time = time.time() - start_time
        
        # Determine location and LLM provider from the result for V3 tracking
        location_detected = detect_location_from_question(question) # Assuming this function uses the original question
        llm_provider = determine_llm_provider(result) # Determine based on which LLM was successful
        
        query_id = None
        if services['database'] and result['success']:
            try:
                # Store the detailed query and analysis in the database
                query_id = services['database'].store_query(
                    question=question,
                    answer=result['final_answer'],
                    question_type=result.get('question_type', 'custom'),
                    processing_time=processing_time,
                    success=result['success'],
                    location_detected=location_detected,
                    llm_provider=llm_provider,
                    confidence_score=result.get('confidence', 0.85), # Default confidence if not in result
                    user_id=user_id
                )
                logger.info(f"💾 Query stored successfully with ID: {query_id} for user: '{user_id}'.")
            except Exception as e:
                logger.error(f"❌ Failed to store query for user '{user_id}': {e}")
        
        response = {
            'success': result['success'],
            'question': question,
            'answer': result['final_answer'],
            'processing_time': round(processing_time, 2),
            'query_id': query_id,
            'user_id': user_id,
            'sources': result.get('sources', {}), # Include source information
            'metadata': {
                'location_detected': location_detected,
                'llm_provider': llm_provider,
                'confidence': result.get('confidence', 0.85),
                'sources_used': {
                    'rss_count': len(result.get('sources', {}).get('rss_sources', [])),
                    'search_count': len(result.get('sources', {}).get('search_sources', [])),
                    'total_sources': result.get('sources', {}).get('total_sources', 0)
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Analysis completed in {processing_time:.2f}s for user '{user_id}'.")
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
                        'type': 'recent_user', # Blue - recent user questions
                        'user_specific': True,
                        'query_id': query_item['id'],
                        'count': 1
                    })
                logger.info(f"✅ Added {len(recent_user_queries)} recent queries for user '{user_id}'.")

                # 2. If user has few recent questions, get their own popular questions
                if len(questions) < 3:
                    user_popular_queries = services['database'].get_popular_questions(limit=3, user_id=user_id)
                    for item in user_popular_queries:
                        # Avoid duplicates
                        if not any(q['question'] == item['question'] for q in questions):
                            questions.append({
                                'question': item['question'],
                                'type': 'popular_user', # Green - user's popular questions
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
                    'type': 'example', # Gray - default examples
                    'user_specific': True, # Now user-specific
                    'query_id': None,
                    'count': 0
                })
            logger.info(f"✅ Added {len(default_questions)} user-specific default questions for '{user_id}'.")
        
        return jsonify({
            'success': True,
            'questions': questions,
            'user_id': user_id,
            'total_count': len(questions),
            'personalization': 'user_specific', # Indicate this is personalized
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
        user_id = request.args.get('user_id')  # Optional user filtering
        
        # Validate and constrain the limit parameter
        if not (1 <= limit <= 1000): # Allow between 1 and 1000 queries
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
        # Attempt to delete the query using the database service
        success = services['database'].delete_query(query_id)
        
        if success:
            logger.info(f"🗑️ Query with ID {query_id} deleted successfully.")
            return jsonify({
                'success': True,
                'message': f"Query {query_id} deleted."
            }), 200 # HTTP 200 OK for successful deletion
        else:
            logger.warning(f"⚠️ Query with ID {query_id} not found or could not be deleted.")
            return jsonify({
                'success': False,
                'error': f"Query with ID {query_id} not found or could not be deleted."
            }), 404 # HTTP 404 Not Found if the query doesn't exist
    except Exception as e:
        logger.error(f"❌ Error deleting query {query_id}: {e}")
        return jsonify({
            'success': False,
            'error': f"Server error while deleting query: {str(e)}"
        }), 500 # HTTP 500 for internal server errors during deletion

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
        
        # Get enhanced database statistics and LLM performance data
        if services['database']:
            try:
                db_stats = services['database'].get_database_stats()
                stats['database'] = db_stats
                
                # Get recent queries to feed into LLM performance analysis function
                recent_queries = services['database'].get_query_history(30) # Fetch up to 30 recent queries
                
                # Analyze LLM performance using the utility function
                llm_performance = analyze_llm_performance(recent_queries)
                stats['llm_performance'] = llm_performance
                
            except Exception as e:
                logger.error(f"Failed to retrieve database or LLM performance stats: {e}")
                stats['database'] = {'error': str(e)}
                stats['llm_performance'] = {'error': str(e)}
        else:
            stats['database'] = {'status': 'not_available'}
            stats['llm_performance'] = {'status': 'not_available'}
        
        # Get LLM provider health status
        if services['llm']:
            try:
                llm_health = services['llm'].get_health_status()
                stats['llm_providers'] = llm_health
            except Exception as e:
                logger.error(f"Failed to retrieve LLM provider health: {e}")
                stats['llm_providers'] = {'error': str(e)}
        
        # Get RSS service status
        if services['rss']:
            try:
                rss_health = services['rss'].get_health_status()
                stats['rss_status'] = rss_health
            except Exception as e:
                logger.error(f"Failed to retrieve RSS service status: {e}")
                stats['rss_status'] = {'error': str(e)}
        
        # Get Web Search service status
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
# DEBUG ENDPOINT (TEMPORARY)
# ================================

@app.route('/debug/queries')
def debug_queries():
    """Temporary endpoint to see what's actually stored in the database by user."""
    if not services['database']:
        return {"error": "Database not available"}
    
    try:
        # Get all queries with user info
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
                'llm_provider': query.get('llm_provider', 'unknown')
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
# These functions support various API routes.
# ================================

def detect_location_from_question(question: str) -> str:
    """
    Detects a specific Australian city or 'National' scope based on keywords in the question.
    This is used for location-aware processing and logging.
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
    
    # Check the llm_provider field first (this is what your property service returns)
    if 'llm_provider' in result:
        return result['llm_provider']
    
    # Fallback to checking nested results
    if result.get('claude_result', {}).get('success', False):
        return 'claude'
    elif result.get('gemini_result', {}).get('success', False):
        return 'gemini'
    else:
        return 'unknown'

# ================================
# GLOBAL ERROR HANDLERS
# These provide consistent JSON error responses for common HTTP status codes.
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
        'available_endpoints': [ # List available endpoints for debugging
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
            'GET /debug/queries'  # Added debug endpoint
        ],
        'details': str(error),
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_server_error_handler(error):
    """Handles HTTP 500 Internal Server Errors."""
    logger.error(f"An unhandled internal server error occurred: {error}", exc_info=True) # Log full traceback
    return jsonify({
        'success': False,
        'error': 'Internal server error. An unexpected condition was encountered.',
        'details': 'Please try again later. If the problem persists, contact support.',
        'timestamp': datetime.now().isoformat()
    }), 500

# ================================
# APPLICATION ENTRY POINT
# This block runs the Flask app when the script is executed directly.
# For production deployments (like Railway using Gunicorn), this block is usually skipped.
# ================================

if __name__ == '__main__':
    # Get port and debug mode from environment variables
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # Log application startup information
    logger.info(f"🚀 Starting Australian Property Intelligence API V3.0")
    logger.info(f"📡 Port: {port}")
    logger.info(f"🔧 Debug Mode: {debug_mode}")
    logger.info(f"🗄️ Database: PostgreSQL + SQLAlchemy")
    logger.info(f"👥 User Switching: Enabled")
    
    # Run the Flask development server if in debug mode.
    # In production (e.g., on Railway with Gunicorn), app.run() is NOT called directly.
    # Gunicorn imports the 'app' object and serves it.
    if debug_mode:
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        # In a production environment, Gunicorn (or another WSGI server)
        # will handle running the application, so we don't need app.run() here.
        # The 'pass' statement simply means do nothing if not in debug mode.
        pass