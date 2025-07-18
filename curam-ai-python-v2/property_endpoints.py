"""
Brisbane Property Intelligence API Endpoints
Add these endpoints to your existing app.py file
"""

from flask import request, jsonify, Response
import json
import logging
from datetime import datetime
from llm_pipeline import BrisbanePropertyPipeline

# Initialize the pipeline
property_pipeline = BrisbanePropertyPipeline()
logger = logging.getLogger(__name__)

# ===== BRISBANE PROPERTY INTELLIGENCE ENDPOINTS =====

@app.route('/api/property/questions', methods=['GET'])
def get_property_questions():
    """Return dropdown questions (preset + popular from database)"""
    try:
        questions = property_pipeline.get_popular_questions(15)
        
        response = {
            'success': True,
            'questions': questions,
            'preset_questions': property_pipeline.get_preset_questions(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Get questions error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/analyze', methods=['POST'])
def analyze_property_question():
    """Main LLM pipeline endpoint"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Determine question type
        preset_questions = property_pipeline.get_preset_questions()
        question_type = 'preset' if question in preset_questions else 'custom'
        
        logger.info(f"Processing property question: {question} (type: {question_type})")
        
        # Process through pipeline and collect all updates
        updates = []
        final_result = None
        
        for update in property_pipeline.process_query(question, question_type):
            updates.append(update)
            if update['status'] == 'complete':
                final_result = update.get('data', {})
        
        # Return complete response
        response = {
            'success': True,
            'question': question,
            'question_type': question_type,
            'processing_updates': updates,
            'final_answer': final_result.get('final_answer', '') if final_result else '',
            'processing_time': final_result.get('processing_time', 0) if final_result else 0,
            'query_id': final_result.get('query_id') if final_result else None,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Property analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/analyze-stream', methods=['POST'])
def analyze_property_stream():
    """Stream processing updates in real-time"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Determine question type
        preset_questions = property_pipeline.get_preset_questions()
        question_type = 'preset' if question in preset_questions else 'custom'
        
        def generate_stream():
            """Generate streaming response"""
            try:
                # Send initial message
                yield f"data: {json.dumps({'status': 'started', 'message': f'Processing: {question}'})}\n\n"
                
                # Process through pipeline
                for update in property_pipeline.process_query(question, question_type):
                    yield f"data: {json.dumps(update)}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'status': 'stream_complete'})}\n\n"
                
            except Exception as e:
                error_update = {
                    'status': 'error',
                    'message': f'Streaming error: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_update)}\n\n"
        
        return Response(
            generate_stream(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        logger.error(f"Property stream error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/history', methods=['GET'])
def get_property_history():
    """Get query history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = property_pipeline.get_query_history(limit)
        
        response = {
            'success': True,
            'history': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/query/<int:query_id>', methods=['GET'])
def get_query_details(query_id):
    """Get detailed information about a specific query"""
    try:
        details = property_pipeline.get_query_details(query_id)
        
        if not details:
            return jsonify({
                'success': False,
                'error': 'Query not found'
            }), 404
        
        response = {
            'success': True,
            'query_details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Get query details error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/reset', methods=['POST'])
def reset_property_session():
    """Reset database/session"""
    try:
        property_pipeline.reset_database()
        
        response = {
            'success': True,
            'message': 'Database reset successfully',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Reset session error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/stats', methods=['GET'])
def get_property_stats():
    """Get database and processing statistics"""
    try:
        stats = property_pipeline.get_database_stats()
        data_sources = property_pipeline.get_data_sources_status()
        
        response = {
            'success': True,
            'stats': stats,
            'data_sources': data_sources,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/email-results', methods=['POST'])
def email_property_results():
    """Email query results to user"""
    try:
        data = request.get_json()
        query_id = data.get('query_id')
        email = data.get('email')
        
        if not query_id or not email:
            return jsonify({
                'success': False,
                'error': 'Query ID and email are required'
            }), 400
        
        # Get query details
        query_details = property_pipeline.get_query_details(query_id)
        if not query_details:
            return jsonify({
                'success': False,
                'error': 'Query not found'
            }), 404
        
        # For now, return success (implement actual email sending later)
        response = {
            'success': True,
            'message': f'Results would be sent to {email}',
            'query_id': query_id,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Email results error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== UPDATE MAIN INDEX ENDPOINT =====

@app.route('/')
def index():
    """Updated main endpoint to reflect Brisbane Property Intelligence"""
    return jsonify({
        'name': 'Brisbane Property Intelligence API',
        'version': '1.0.0',
        'description': 'Multi-LLM Brisbane property analysis with Claude, Gemini, and real-time data scraping',
        'endpoints': {
            'health': '/health',
            'property_questions': 'GET /api/property/questions',
            'property_analyze': 'POST /api/property/analyze',
            'property_stream': 'POST /api/property/analyze-stream',
            'property_history': 'GET /api/property/history',
            'property_query_details': 'GET /api/property/query/<id>',
            'property_reset': 'POST /api/property/reset',
            'property_stats': 'GET /api/property/stats',
            'email_results': 'POST /api/property/email-results'
        },
        'status': 'running',
        'features': [
            'Multi-LLM Analysis (Claude + Gemini)',
            'Real-time Brisbane Property Data',
            'Query History & Analytics',
            'Streaming Progress Updates',
            'Brisbane-specific Insights'
        ],
        'ai_services': {
            'claude': 'Available' if property_pipeline.claude_client else 'Mock Mode',
            'gemini': 'Available' if property_pipeline.gemini_model else 'Mock Mode',
            'data_scraping': 'Active'
        },
        'preset_questions': property_pipeline.get_preset_questions(),
        'data_sources': [
            'Brisbane City Council RSS',
            'Property Observer Brisbane',
            'RealEstate.com.au News',
            'Queensland Government Data'
        ]
    })

# ===== HEALTH CHECK UPDATE =====

@app.route('/health')
def health():
    """Updated health check for Brisbane Property Intelligence"""
    try:
        logger.info("Health check requested")
        
        # Test database connection
        try:
            stats = property_pipeline.get_database_stats()
            database_status = True
        except Exception as e:
            database_status = False
            logger.error(f"Database health check failed: {str(e)}")
        
        # Test LLM connections
        claude_status = property_pipeline.claude_client is not None
        gemini_status = property_pipeline.gemini_model is not None
        
        response_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version.split()[0],
            'services': {
                'flask': True,
                'database': database_status,
                'claude': claude_status,
                'gemini': gemini_status,
                'data_scraping': True
            },
            'database_stats': stats if database_status else {},
            'environment': {
                'claude_api_configured': bool(os.getenv('CLAUDE_API_KEY')),
                'gemini_api_configured': bool(os.getenv('GEMINI_API_KEY'))
            }
        }
        
        # Test core libraries
        try:
            response_data['flask_version'] = Flask.__version__
            response_data['pandas_version'] = pd.__version__
            response_data['requests_version'] = requests.__version__
        except Exception as e:
            response_data['library_error'] = str(e)
        
        overall_status = all([
            response_data['services']['flask'],
            response_data['services']['database']
        ])
        
        if not overall_status:
            response_data['status'] = 'degraded'
        
        status_code = 200 if overall_status else 503
        
        logger.info(f"Health check completed: {response_data['status']}")
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500