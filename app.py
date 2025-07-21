"""
Australian Property Intelligence API V3
Professional Flask application with PostgreSQL + User Switching
UPDATED: Clean architecture with user switching functionality
"""

import os
import sys
import logging
import time
import queue
import json
import threading
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_with_context # Ensure Response and stream_with_context are imported
from flask_cors import CORS # This import was also part of the concatenated line, moved here

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # Define logger for this module here!
log_queue = queue.Queue() # This line should end here, without concatenation


class QueueHandler(logging.Handler):
    """
    A custom logging handler that puts log records into a queue.
    These records can then be picked up by an SSE endpoint.
    """
    def emit(self, record):
        try:
            # Format the log record into a dictionary
            # Includes timestamp for client-side display consistency
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
                "level": record.levelname,
                "message": self.format(record),
                "name": record.name # Logger name (e.g., __main__, services.llm_service)
            }
            # Put the JSON string into the queue
            log_queue.put(json.dumps(log_entry))
        except Exception:
            self.handleError(record)

# Set up logging FIRST, before using logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # Define logger for this module here!

# --- Attach the custom handler to the root logger ---
# This ensures all logs from Flask, your services, etc., go into the queue.
logging.getLogger().addHandler(QueueHandler())
logger.info("✅ Live log stream handler initialized and attached to root logger.")


# Import professional services
from config import Config
from services import LLMService, PropertyAnalysisService
from enhanced_database import PropertyDatabase
from utils import HealthChecker

app = Flask(__name__)

# Configure CORS
CORS(app, origins=Config.CORS_ORIGINS)

def initialize_services():
    """Initialize all services with proper error handling"""
    services = {}
    
    # Log configuration status
    Config.log_config_status()
    
    # Database (V3 PostgreSQL)
    try:
        services['database'] = PropertyDatabase()
        logger.info("✅ PostgreSQL database service initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        services['database'] = None
    
    # LLM Service
    try:
        services['llm'] = LLMService()
        logger.info("✅ LLM service initialized")
    except Exception as e:
        logger.error(f"❌ LLM service initialization failed: {e}")
        services['llm'] = None
    
    # RSS Service for Australian Property Data
    try:
        from services.rss_service import RSSService
        services['rss'] = RSSService()
        logger.info("✅ RSS service initialized")
    except Exception as e:
        logger.error(f"❌ RSS service initialization failed: {e}")
        services['rss'] = None
    
    # Property Analysis Service
    if services['llm']:
        try:
            services['property'] = PropertyAnalysisService(services['llm'], services['rss'])
            logger.info("✅ Property analysis service initialized")
        except Exception as e:
            logger.error(f"❌ Property service initialization failed: {e}")
            services['property'] = None
    else:
        services['property'] = None
    
    # Health Checker
    try:
        services['health'] = HealthChecker(services)
        logger.info("✅ Health checker initialized")
    except Exception as e:
        logger.error(f"❌ Health checker initialization failed: {e}")
        services['health'] = None
    
    # Log service summary
    available_services = [name for name, service in services.items() if service is not None]
    logger.info(f"🚀 Services initialized: {', '.join(available_services)}")
    
    return services

# Initialize services
services = initialize_services()

def analyze_llm_performance(recent_queries):
    """Analyze LLM performance from recent queries for dashboard charts"""
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
        
        # Response times for line chart (last 10 queries)
        response_times = []
        for query in recent_queries[-10:]:
            response_times.append({
                'query_id': query.get('id', 0),
                'processing_time': query.get('processing_time', 0),
                'timestamp': query.get('created_at', '')
            })
        
        # Provider performance comparison (using actual data from V3 database)
        claude_queries = [q for q in recent_queries if q.get('llm_provider') == 'claude']
        gemini_queries = [q for q in recent_queries if q.get('llm_provider') == 'gemini']
        
        claude_times = [q['processing_time'] for q in claude_queries if q.get('processing_time')]
        gemini_times = [q['processing_time'] for q in gemini_queries if q.get('processing_time')]
        
        provider_performance = {
            'claude': {
                'avg_response_time': round(sum(claude_times) / len(claude_times), 2) if claude_times else 0,
                'success_rate': round(sum(1 for q in claude_queries if q.get('success', True)) / len(claude_queries) * 100, 1) if claude_queries else 100,
                'total_queries': len(claude_queries)
            },
            'gemini': {
                'avg_response_time': round(sum(gemini_times) / len(gemini_times), 2) if gemini_times else 0,
                'success_rate': round(sum(1 for q in gemini_queries if q.get('success', True)) / len(gemini_queries) * 100, 1) if gemini_queries else 100,
                'total_queries': len(gemini_queries)
            }
        }
        
        # Location breakdown using V3 location_detected field
        location_breakdown = {}
        for query in recent_queries:
            location = query.get('location_detected', 'National')
            location_breakdown[location] = location_breakdown.get(location, 0) + 1
        
        # Success rates
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

# ================================
# MAIN API ROUTES
# ================================

@app.route('/')
def index():
    """Australian Property Intelligence API V3 information"""
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
            'Enhanced Performance Monitoring'
        ],
        'services': services['health'].get_service_status() if services['health'] else {},
        'api_endpoints': {
            'analyze': 'POST /api/property/analyze',
            'questions': 'GET /api/property/questions',
            'history': 'GET /api/property/history',
            'stats': 'GET /api/property/stats',
            'users': 'GET /api/users',
            'user_stats': 'GET /api/users/{user_id}/stats',
            'user_history': 'GET /api/users/{user_id}/history',
            'health': 'GET /health',
            'stream_logs': 'GET /stream_logs' # Added this for completeness
        }
    })

@app.route('/health')
def health():
    """Comprehensive health check"""
    if not services['health']:
        return jsonify({
            'status': 'error',
            'error': 'Health checker not available',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    return jsonify(services['health'].get_comprehensive_health())

# ================================
# USER SWITCHING API ROUTES (NEW)
# ================================

@app.route('/api/users', methods=['GET'])
def get_demo_users():
    """Get available demo users for switching"""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database not available'
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
        logger.error(f"Get demo users error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<user_id>/stats', methods=['GET'])
def get_user_statistics(user_id: str):
    """Get comprehensive statistics for a specific user"""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 500
    
    try:
        stats = services['database'].get_user_stats(user_id)
        
        if not stats:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get user statistics error for {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<user_id>/history', methods=['GET'])
def get_user_history(user_id: str):
    """Get query history for a specific user"""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 500
    
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Validate parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 5
        
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
        logger.error(f"Get user history error for {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# PROPERTY ANALYSIS ROUTES
# ================================

@app.route('/api/property/analyze', methods=['POST'])
def analyze_property_question():
    """Analyze Australian property question with user tracking"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body must be JSON'
            }), 400
        
        question = data.get('question', '').strip()
        user_id = data.get('user_id', 'anonymous')  # NEW: User tracking
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        if not services['property']:
            return jsonify({
                'success': False,
                'error': 'Property analysis service not available'
            }), 500
        
        logger.info(f"🔍 Processing property question for user {user_id}: {question}")
        start_time = time.time()
        
        # Use professional property analysis service
        result = services['property'].analyze_property_question(question)
        processing_time = time.time() - start_time
        
        # Detect location and LLM provider for V3 tracking
        location_detected = detect_location_from_question(question)
        llm_provider = determine_llm_provider(result)
        
        # Store in database with enhanced V3 fields
        query_id = None
        if services['database'] and result['success']:
            try:
                query_id = services['database'].store_query(
                    question=question,
                    answer=result['final_answer'],
                    question_type=result.get('question_type', 'custom'),
                    processing_time=processing_time,
                    success=result['success'],
                    # V3 enhanced fields
                    location_detected=location_detected,
                    llm_provider=llm_provider,
                    confidence_score=result.get('confidence', 0.85),
                    user_id=user_id
                )
                logger.info(f"💾 Query stored with ID: {query_id} for user: {user_id}")
            except Exception as e:
                logger.error(f"Failed to store query: {e}")
        
        response = {
            'success': result['success'],
            'question': question,
            'answer': result['final_answer'],
            'processing_time': round(processing_time, 2),
            'query_id': query_id,
            'user_id': user_id,
            'metadata': {
                'location_detected': location_detected,
                'llm_provider': llm_provider,
                'confidence': result.get('confidence', 0.85)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Analysis completed in {processing_time:.2f}s for user {user_id}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Property analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/property/questions', methods=['GET'])
def get_property_questions():
    """Get preset questions (can be customized per user in future)"""
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        # Get user-specific preset questions
        preset_questions = get_user_preset_questions(user_id)
        
        questions = []
        for question in preset_questions:
            questions.append({
                'question': question,
                'type': 'preset',
                'user_specific': user_id != 'anonymous'
            })
        
        # Add popular questions from database for this user
        if services['database']:
            try:
                popular = services['database'].get_popular_questions(5, user_id if user_id != 'anonymous' else None)
                for item in popular:
                    if item['question'] not in preset_questions:
                        questions.append({
                            'question': item['question'],
                            'type': 'popular',
                            'count': item['count'],
                            'user_specific': user_id != 'anonymous'
                        })
            except Exception as e:
                logger.error(f"Failed to get popular questions: {e}")
        
        return jsonify({
            'success': True,
            'questions': questions,
            'user_id': user_id,
            'total_count': len(questions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get questions error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/history', methods=['GET'])
def get_property_history():
    """Get query history (all users or filtered)"""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 500
    
    try:
        limit = request.args.get('limit', 50, type=int)
        user_id = request.args.get('user_id')  # Optional user filtering
        
        # Validate parameters
        if limit > 1000:
            limit = 1000
        if limit < 1:
            limit = 10
        
        history = services['database'].get_query_history(limit=limit, user_id=user_id)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'limit': limit,
            'user_filter': user_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/stats', methods=['GET'])
def get_property_stats():
    """Get comprehensive system statistics with enhanced V3 analytics"""
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'version': '3.0.0',
                'python_version': sys.version.split()[0],
                'database_type': 'PostgreSQL + SQLAlchemy'
            }
        }
        
        # Enhanced database stats
        if services['database']:
            try:
                db_stats = services['database'].get_database_stats()
                stats['database'] = db_stats
                
                # Get recent queries for LLM performance analysis
                recent_queries = services['database'].get_query_history(30)
                
                # Enhanced LLM performance data
                llm_performance = analyze_llm_performance(recent_queries)
                stats['llm_performance'] = llm_performance
                
            except Exception as e:
                stats['database'] = {'error': str(e)}
                stats['llm_performance'] = {'error': str(e)}
        else:
            stats['database'] = {'status': 'not_available'}
            stats['llm_performance'] = {'status': 'not_available'}
        
        # LLM provider health
        if services['llm']:
            try:
                llm_health = services['llm'].get_health_status()
                stats['llm_providers'] = llm_health
            except Exception as e:
                stats['llm_providers'] = {'error': str(e)}
        
        # RSS service stats
        if services['rss']:
            try:
                rss_health = services['rss'].get_health_status()
                stats['rss_status'] = rss_health
            except Exception as e:
                stats['rss_status'] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# UTILITY FUNCTIONS
# ================================

def detect_location_from_question(question: str) -> str:
    """Detect location from question text"""
    if not question:
        return 'National'
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['brisbane', 'queensland', 'qld']):
        return 'Brisbane'
    elif any(word in question_lower for word in ['sydney', 'nsw']):
        return 'Sydney'
    elif any(word in question_lower for word in ['melbourne', 'victoria', 'vic']):
        return 'Melbourne'
    elif any(word in question_lower for word in ['perth', 'western australia', 'wa']):
        return 'Perth'
    else:
        return 'National'

def determine_llm_provider(result: dict) -> str:
    """Determine which LLM provider was used"""
    # This would be enhanced based on your actual LLM service implementation
    # For now, simple detection based on result structure
    if result.get('claude_result', {}).get('success', False):
        return 'claude'
    elif result.get('gemini_result', {}).get('success', False):
        return 'gemini'
    else:
        return 'unknown'

def get_user_preset_questions(user_id: str) -> list:
    """Get user-specific preset questions"""
    user_presets = {
        'sarah_buyer': [
            "Best suburbs under $600k for first home buyers in Brisbane",
            "Units near train stations in Brisbane",
            "First home buyer grants and assistance",
            "Safest affordable suburbs for young professionals"
        ],
        'michael_investor': [
            "High rental yield suburbs in Brisbane",
            "Investment property hotspots 2025",
            "Logan vs Ipswich for property investment",
            "Brisbane outer suburbs with growth potential"
        ]
    }
    
    return user_presets.get(user_id, Config.PRESET_QUESTIONS)

# ================================
# ERROR HANDLERS
# ================================

@app.errorhandler(400)
def bad_request(error):
    # This handler catches explicit abort(400) calls or validation errors in Flask
    # It might not catch all JSON parsing errors if they happen before request.get_json()
    return jsonify({
        'success': False,
        'error': 'Bad Request: ' + str(error),
        'timestamp': datetime.now().isoformat()
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'GET /health',
            'GET /stream_logs', # Added this for completeness
            'GET /api/users',
            'GET /api/users/{user_id}/stats',
            'GET /api/users/{user_id}/history',
            'GET /api/property/questions',
            'POST /api/property/analyze',
            'GET /api/property/history',
            'GET /api/property/stats'
        ],
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # Start the application
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Australian Property Intelligence API V3.0")
    logger.info(f"📡 Port: {port}")
    logger.info(f"🔧 Debug: {debug_mode}")
    logger.info(f"🗄️ Database: PostgreSQL + SQLAlchemy")
    logger.info(f"👥 User Switching: Enabled")
    
    # When using gunicorn (as in railway.json), app.run() is not typically called here.
    # The gunicorn command in railway.json handles starting the app.
    # So this block is primarily for local dev without gunicorn.
    if debug_mode:
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        # In production, gunicorn is used, so we don't call app.run() directly.
        # But for completeness, a non-debug run can be included if not using gunicorn.
        pass

class QueueHandler(logging.Handler):
    """
    A custom logging handler that puts log records into a queue.
    These records can then be picked up by an SSE endpoint.
    """
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

# --- Attach the custom handler to the root logger ---
# This ensures all logs from Flask, your services, etc., go into the queue.
# It should be called after logging.basicConfig and logger is defined.
logging.getLogger().addHandler(QueueHandler())
logger.info("✅ Live log stream handler initialized and attached to root logger.") # This line will now work

# Import professional services (these can stay where they are)
from config import Config
from services import LLMService, PropertyAnalysisService
from enhanced_database import PropertyDatabase
from utils import HealthChecker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS
CORS(app, origins=Config.CORS_ORIGINS)

def initialize_services():
    """Initialize all services with proper error handling"""
    services = {}
    
    # Log configuration status
    Config.log_config_status()
    
    # Database (V3 PostgreSQL)
    try:
        services['database'] = PropertyDatabase()
        logger.info("✅ PostgreSQL database service initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        services['database'] = None
    
    # LLM Service
    try:
        services['llm'] = LLMService()
        logger.info("✅ LLM service initialized")
    except Exception as e:
        logger.error(f"❌ LLM service initialization failed: {e}")
        services['llm'] = None
    
    # RSS Service for Australian Property Data
    try:
        from services.rss_service import RSSService
        services['rss'] = RSSService()
        logger.info("✅ RSS service initialized")
    except Exception as e:
        logger.error(f"❌ RSS service initialization failed: {e}")
        services['rss'] = None
    
    # Property Analysis Service
    if services['llm']:
        try:
            services['property'] = PropertyAnalysisService(services['llm'], services['rss'])
            logger.info("✅ Property analysis service initialized")
        except Exception as e:
            logger.error(f"❌ Property service initialization failed: {e}")
            services['property'] = None
    else:
        services['property'] = None
    
    # Health Checker
    try:
        services['health'] = HealthChecker(services)
        logger.info("✅ Health checker initialized")
    except Exception as e:
        logger.error(f"❌ Health checker initialization failed: {e}")
        services['health'] = None
    
    # Log service summary
    available_services = [name for name, service in services.items() if service is not None]
    logger.info(f"🚀 Services initialized: {', '.join(available_services)}")
    
    return services

# Initialize services
services = initialize_services()

def analyze_llm_performance(recent_queries):
    """Analyze LLM performance from recent queries for dashboard charts"""
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
        
        # Response times for line chart (last 10 queries)
        response_times = []
        for query in recent_queries[-10:]:
            response_times.append({
                'query_id': query.get('id', 0),
                'processing_time': query.get('processing_time', 0),
                'timestamp': query.get('created_at', '')
            })
        
        # Provider performance comparison (using actual data from V3 database)
        claude_queries = [q for q in recent_queries if q.get('llm_provider') == 'claude']
        gemini_queries = [q for q in recent_queries if q.get('llm_provider') == 'gemini']
        
        claude_times = [q['processing_time'] for q in claude_queries if q.get('processing_time')]
        gemini_times = [q['processing_time'] for q in gemini_queries if q.get('processing_time')]
        
        provider_performance = {
            'claude': {
                'avg_response_time': round(sum(claude_times) / len(claude_times), 2) if claude_times else 0,
                'success_rate': round(sum(1 for q in claude_queries if q.get('success', True)) / len(claude_queries) * 100, 1) if claude_queries else 100,
                'total_queries': len(claude_queries)
            },
            'gemini': {
                'avg_response_time': round(sum(gemini_times) / len(gemini_times), 2) if gemini_times else 0,
                'success_rate': round(sum(1 for q in gemini_queries if q.get('success', True)) / len(gemini_queries) * 100, 1) if gemini_queries else 100,
                'total_queries': len(gemini_queries)
            }
        }
        
        # Location breakdown using V3 location_detected field
        location_breakdown = {}
        for query in recent_queries:
            location = query.get('location_detected', 'National')
            location_breakdown[location] = location_breakdown.get(location, 0) + 1
        
        # Success rates
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

# ================================
# MAIN API ROUTES
# ================================

@app.route('/')
def index():
    """Australian Property Intelligence API V3 information"""
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
            'Professional Error Handling'
        ],
        'services': services['health'].get_service_status() if services['health'] else {},
        'api_endpoints': {
            'analyze': 'POST /api/property/analyze',
            'questions': 'GET /api/property/questions',
            'history': 'GET /api/property/history',
            'stats': 'GET /api/property/stats',
            'users': 'GET /api/users',
            'user_stats': 'GET /api/users/{user_id}/stats',
            'user_history': 'GET /api/users/{user_id}/history',
            'health': 'GET /health'
        }
    })

@app.route('/health')
def health():
    """Comprehensive health check"""
    if not services['health']:
        return jsonify({
            'status': 'error',
            'error': 'Health checker not available',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    return jsonify(services['health'].get_comprehensive_health())

# ================================
# USER SWITCHING API ROUTES (NEW)
# ================================

@app.route('/api/users', methods=['GET'])
def get_demo_users():
    """Get available demo users for switching"""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database not available'
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
        logger.error(f"Get demo users error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<user_id>/stats', methods=['GET'])
def get_user_statistics(user_id: str):
    """Get comprehensive statistics for a specific user"""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 500
    
    try:
        stats = services['database'].get_user_stats(user_id)
        
        if not stats:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get user statistics error for {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<user_id>/history', methods=['GET'])
def get_user_history(user_id: str):
    """Get query history for a specific user"""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 500
    
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Validate parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 5
        
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
        logger.error(f"Get user history error for {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# PROPERTY ANALYSIS ROUTES
# ================================

@app.route('/api/property/analyze', methods=['POST'])
def analyze_property_question():
    """Analyze Australian property question with user tracking"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body must be JSON'
            }), 400
        
        question = data.get('question', '').strip()
        user_id = data.get('user_id', 'anonymous')  # NEW: User tracking
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        if not services['property']:
            return jsonify({
                'success': False,
                'error': 'Property analysis service not available'
            }), 500
        
        logger.info(f"🔍 Processing property question for user {user_id}: {question}")
        start_time = time.time()
        
        # Use professional property analysis service
        result = services['property'].analyze_property_question(question)
        processing_time = time.time() - start_time
        
        # Detect location and LLM provider for V3 tracking
        location_detected = detect_location_from_question(question)
        llm_provider = determine_llm_provider(result)
        
        # Store in database with enhanced V3 fields
        query_id = None
        if services['database'] and result['success']:
            try:
                query_id = services['database'].store_query(
                    question=question,
                    answer=result['final_answer'],
                    question_type=result.get('question_type', 'custom'),
                    processing_time=processing_time,
                    success=result['success'],
                    # V3 enhanced fields
                    location_detected=location_detected,
                    llm_provider=llm_provider,
                    confidence_score=result.get('confidence', 0.85),
                    user_id=user_id
                )
                logger.info(f"💾 Query stored with ID: {query_id} for user: {user_id}")
            except Exception as e:
                logger.error(f"Failed to store query: {e}")
        
        response = {
            'success': result['success'],
            'question': question,
            'answer': result['final_answer'],
            'processing_time': round(processing_time, 2),
            'query_id': query_id,
            'user_id': user_id,
            'metadata': {
                'location_detected': location_detected,
                'llm_provider': llm_provider,
                'confidence': result.get('confidence', 0.85)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Analysis completed in {processing_time:.2f}s for user {user_id}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Property analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/property/questions', methods=['GET'])
def get_property_questions():
    """
    Get dynamic property questions based on user history and popular queries.
    Provides fallback to default examples if no history exists.
    """
    try:
        user_id = request.args.get('user_id', 'anonymous')
        questions = []
        
        # Try to get recent queries for the specific user
        if services['database']:
            try:
                # Fetch recent queries for the user
                recent_user_queries = services['database'].get_query_history(limit=5, user_id=user_id)
                for query_item in recent_user_queries:
                    questions.append({
                        'question': query_item['question'],
                        'type': 'recent_user',
                        'user_specific': True,
                        'query_id': query_item['id'],
                        'count': 1 # Placeholder for count, as it's from history
                    })
                logger.info(f"Retrieved {len(recent_user_queries)} recent queries for user {user_id}.")

                # Fetch overall popular queries (not user-specific for broad examples)
                popular_global_queries = services['database'].get_popular_questions(limit=5, user_id=None) # Pass None for global
                for item in popular_global_queries:
                    # Avoid duplicates if a popular question is also a recent user question
                    if not any(q['question'] == item['question'] for q in questions):
                        questions.append({
                            'question': item['question'],
                            'type': 'popular_global',
                            'user_specific': False,
                            'count': item['count']
                        })
                logger.info(f"Retrieved {len(popular_global_queries)} popular global queries.")

            except Exception as e:
                logger.error(f"Failed to retrieve dynamic questions from database: {e}")
        
        # If no dynamic questions are found, use default examples from Config
        if not questions:
            for question_text in Config.DEFAULT_EXAMPLE_QUESTIONS:
                questions.append({
                    'question': question_text,
                    'type': 'example',
                    'user_specific': False
                })
            logger.info("Using default example questions as no dynamic questions found.")
        
        return jsonify({
            'success': True,
            'questions': questions,
            'user_id': user_id,
            'total_count': len(questions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get questions error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/history', methods=['GET'])
def get_property_history():
    """Get query history (all users or filtered)"""
    if not services['database']:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 500
    
    try:
        limit = request.args.get('limit', 50, type=int)
        user_id = request.args.get('user_id')  # Optional user filtering
        
        # Validate parameters
        if limit > 1000:
            limit = 1000
        if limit < 1:
            limit = 10
        
        history = services['database'].get_query_history(limit=limit, user_id=user_id)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'limit': limit,
            'user_filter': user_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/stats', methods=['GET'])
def get_property_stats():
    """Get comprehensive system statistics with enhanced V3 analytics"""
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'version': '3.0.0',
                'python_version': sys.version.split()[0],
                'database_type': 'PostgreSQL + SQLAlchemy'
            }
        }
        
        # Enhanced database stats
        if services['database']:
            try:
                db_stats = services['database'].get_database_stats()
                stats['database'] = db_stats
                
                # Get recent queries for LLM performance analysis
                recent_queries = services['database'].get_query_history(30)
                
                # Enhanced LLM performance data
                llm_performance = analyze_llm_performance(recent_queries)
                stats['llm_performance'] = llm_performance
                
            except Exception as e:
                stats['database'] = {'error': str(e)}
                stats['llm_performance'] = {'error': str(e)}
        else:
            stats['database'] = {'status': 'not_available'}
            stats['llm_performance'] = {'status': 'not_available'}
        
        # LLM provider health
        if services['llm']:
            try:
                llm_health = services['llm'].get_health_status()
                stats['llm_providers'] = llm_health
            except Exception as e:
                stats['llm_providers'] = {'error': str(e)}
        
        # RSS service stats
        if services['rss']:
            try:
                rss_health = services['rss'].get_health_status()
                stats['rss_status'] = rss_health
            except Exception as e:
                stats['rss_status'] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# UTILITY FUNCTIONS
# ================================

def detect_location_from_question(question: str) -> str:
    """Detect location from question text"""
    if not question:
        return 'National'
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['brisbane', 'queensland', 'qld']):
        return 'Brisbane'
    elif any(word in question_lower for word in ['sydney', 'nsw']):
        return 'Sydney'
    elif any(word in question_lower for word in ['melbourne', 'victoria', 'vic']):
        return 'Melbourne'
    elif any(word in question_lower for word in ['perth', 'western australia', 'wa']):
        return 'Perth'
    else:
        return 'National'

def determine_llm_provider(result: dict) -> str:
    """Determine which LLM provider was used"""
    # This would be enhanced based on your actual LLM service implementation
    # For now, simple detection based on result structure
    if 'claude' in str(result).lower():
        return 'claude'
    elif 'gemini' in str(result).lower():
        return 'gemini'
    else:
        return 'claude'  # Default

def get_user_preset_questions(user_id: str) -> list:
    """Get user-specific preset questions"""
    user_presets = {
        'sarah_buyer': [
            "Best suburbs under $600k for first home buyers in Brisbane",
            "Units near train stations in Brisbane",
            "First home buyer grants and assistance",
            "Safest affordable suburbs for young professionals"
        ],
        'michael_investor': [
            "High rental yield suburbs in Brisbane",
            "Investment property hotspots 2025",
            "Logan vs Ipswich for property investment",
            "Brisbane outer suburbs with growth potential"
        ]
    }
    
    return user_presets.get(user_id, Config.PRESET_QUESTIONS)

# ================================
# ERROR HANDLERS
# ================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'GET /health',
            'GET /api/users',
            'GET /api/users/{user_id}/stats',
            'GET /api/users/{user_id}/history',
            'GET /api/property/questions',
            'POST /api/property/analyze',
            'GET /api/property/history',
            'GET /api/property/stats'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # Start the application
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Australian Property Intelligence API V3.0")
    logger.info(f"📡 Port: {port}")
    logger.info(f"🔧 Debug: {debug_mode}")
    logger.info(f"🗄️ Database: PostgreSQL + SQLAlchemy")
    logger.info(f"👥 User Switching: Enabled")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)




@app.route('/stream_logs')
def stream_logs():
    """
    SSE endpoint to stream real-time log messages to connected clients.
    """
    def generate():
        while True:
            try:
                # Get log message from queue with a timeout.
                # A timeout prevents the generator from blocking indefinitely if no logs.
                # A small timeout (e.g., 1 second) is good practice.
                log_message = log_queue.get(timeout=1)
                yield f"data: {log_message}\n\n"
            except queue.Empty:
                # If the queue is empty, send a "keep-alive" comment or empty data.
                # This prevents the client's connection from timing out.
                # An empty JSON object `data: {}\n\n` is also a valid keep-alive signal.
                yield "data: {}\n\n"
            except Exception as e:
                # Log any errors occurring within the generator itself
                logger.error(f"Error in log stream generator: {e}")
                # Optionally, send an error message to the client through the stream
                yield f"data: {json.dumps({'level': 'ERROR', 'message': f'Server stream error: {e}'})}\n\n"
            
            # Small delay to prevent tight looping and high CPU usage if logs are very frequent
            time.sleep(0.05) # 50 milliseconds

    # Return the response with the event-stream mimetype
    return Response(stream_with_context(generate()), mimetype="text/event-stream")



# ================================
# Managing Questions
# ================================


    @app.route('/api/property/history/<int:query_id>', methods=['DELETE'])
def delete_query_by_id(query_id: int):
    """Delete a specific query from history by its ID."""
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
            'error': f"Server error deleting query: {str(e)}"
        }), 500