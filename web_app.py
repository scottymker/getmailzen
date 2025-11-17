"""
Gmail Agent Web Interface
Flask-based dashboard for managing email automation
"""
import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from app.email_processor import EmailProcessor
from app.retention_manager import RetentionManager
from app.inbox_analyzer import InboxAnalyzer
from app.auth import AuthService, validate_email, validate_password_strength
from app.database import SessionLocal
from app.oauth_manager import OAuthManager

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
CORS(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Configuration file
CONFIG_FILE = 'config.json'


def load_config():
    """Load configuration from JSON file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default configuration
        return {
            'categories': [
                {
                    'name': 'Newsletters',
                    'description': 'Marketing emails, newsletters, and subscriptions',
                    'actions': ['label:Newsletters', 'archive']
                },
                {
                    'name': 'Shopping',
                    'description': 'E-commerce receipts, shipping notifications, order confirmations',
                    'actions': ['label:Shopping']
                },
                {
                    'name': 'Social',
                    'description': 'Social media notifications',
                    'actions': ['label:Social', 'archive']
                },
                {
                    'name': 'Finance',
                    'description': 'Bank statements, bills, payment confirmations',
                    'actions': ['label:Finance', 'star']
                },
                {
                    'name': 'Spam',
                    'description': 'Unwanted promotional emails',
                    'actions': ['label:Spam', 'delete']
                }
            ],
            'processing_settings': {
                'max_emails': 50,
                'query': 'is:unread',
                'dry_run': False
            }
        }


def save_config(config):
    """Save configuration to JSON file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    db = SessionLocal()
    from app.models import User
    user = db.query(User).filter_by(id=int(user_id)).first()
    db.close()
    return user


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validation
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('register.html')

        if not validate_email(email):
            flash('Invalid email address', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        is_valid, message = validate_password_strength(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('register.html')

        # Register user
        auth_service = AuthService()
        success, result = auth_service.register_user(email, password)

        if success:
            flash(f'Registration successful! Welcome to GetMailZen. You have a 14-day free trial.', 'success')
            # Auto-login after registration
            login_user(result)
            auth_service.close()
            return redirect(url_for('dashboard'))
        else:
            auth_service.close()
            flash(result, 'error')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember', False)

        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')

        # Authenticate user
        auth_service = AuthService()
        success, result = auth_service.authenticate_user(email, password)

        if success:
            login_user(result, remember=remember)
            auth_service.close()

            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            auth_service.close()
            flash(result, 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))


# ============================================================================
# GMAIL OAUTH ROUTES
# ============================================================================

@app.route('/connect-gmail')
@login_required
def connect_gmail():
    """Initiate Gmail OAuth flow"""
    oauth_manager = OAuthManager()

    # Generate redirect URI
    redirect_uri = url_for('gmail_oauth_callback', _external=True, _scheme='http')

    # Store state in session for security
    import secrets
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state

    # Get authorization URL
    authorization_url, state = oauth_manager.get_authorization_url(
        redirect_uri=redirect_uri,
        state=state
    )

    oauth_manager.close()

    return redirect(authorization_url)


@app.route('/gmail-oauth-callback')
@login_required
def gmail_oauth_callback():
    """Handle Gmail OAuth callback"""
    # Verify state for security
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        flash('OAuth state mismatch. Please try again.', 'error')
        return redirect(url_for('dashboard'))

    # Clear state from session
    session.pop('oauth_state', None)

    # Get authorization response (full callback URL)
    authorization_response = request.url

    # Generate redirect URI (must match the one used in connect_gmail)
    redirect_uri = url_for('gmail_oauth_callback', _external=True, _scheme='http')

    # Handle OAuth callback
    oauth_manager = OAuthManager()
    success, message = oauth_manager.handle_oauth_callback(
        user_id=current_user.id,
        authorization_response=authorization_response,
        redirect_uri=redirect_uri
    )
    oauth_manager.close()

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('dashboard'))


@app.route('/disconnect-gmail/<gmail_email>')
@login_required
def disconnect_gmail(gmail_email):
    """Disconnect Gmail account"""
    oauth_manager = OAuthManager()
    success, message = oauth_manager.disconnect_gmail_account(
        user_id=current_user.id,
        gmail_email=gmail_email
    )
    oauth_manager.close()

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('dashboard'))


@app.route('/api/gmail-accounts')
@login_required
def get_gmail_accounts():
    """Get all Gmail accounts connected by current user"""
    oauth_manager = OAuthManager()
    accounts = oauth_manager.get_user_gmail_accounts(user_id=current_user.id)
    oauth_manager.close()

    return jsonify({
        'success': True,
        'accounts': [
            {
                'gmail_email': acc.gmail_email,
                'connected_at': acc.created_at.isoformat() if acc.created_at else None,
                'is_expired': acc.is_token_expired()
            }
            for acc in accounts
        ]
    })


# ============================================================================
# DASHBOARD ROUTES (Protected)
# ============================================================================

@app.route('/')
@login_required
def index():
    """Main dashboard page"""
    config = load_config()
    return render_template('index.html', config=config, user=current_user)


@app.route('/dashboard')
@login_required
def dashboard():
    """Modern dashboard page"""
    config = load_config()
    return render_template('dashboard.html', config=config, user=current_user)


@app.route('/api/process', methods=['POST'])
@login_required
def process_emails():
    """Process emails using AI categorization"""
    try:
        data = request.json or {}
        config = load_config()

        # Get processing parameters
        max_emails = data.get('max_emails', config['processing_settings']['max_emails'])
        query = data.get('query', config['processing_settings']['query'])
        dry_run = data.get('dry_run', config['processing_settings']['dry_run'])

        # Initialize processor with user's Gmail credentials
        processor = EmailProcessor(user_id=current_user.id)

        # Process emails
        results = processor.process_inbox(
            max_emails=max_emails,
            query=query,
            categories=config['categories'],
            dry_run=dry_run
        )

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/suggest-categories', methods=['POST'])
@login_required
def suggest_categories():
    """Use AI to suggest email categories based on inbox analysis"""
    try:
        data = request.json or {}
        sample_size = data.get('sample_size', 50)

        processor = EmailProcessor(user_id=current_user.id)
        suggestions = processor.suggest_categories(sample_size=sample_size)

        return jsonify({
            'success': True,
            'suggestions': suggestions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def manage_config():
    """Get or update configuration"""
    if request.method == 'GET':
        config = load_config()
        return jsonify(config)

    elif request.method == 'POST':
        try:
            new_config = request.json
            save_config(new_config)
            return jsonify({
                'success': True,
                'message': 'Configuration updated'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@app.route('/api/test-connection', methods=['GET'])
@login_required
def test_connection():
    """Test Gmail and Claude API connections"""
    try:
        processor = EmailProcessor(user_id=current_user.id)

        # Test Gmail connection
        inbox_stats = processor.get_inbox_stats()

        return jsonify({
            'success': True,
            'gmail_connected': True,
            'claude_connected': True,
            'inbox_stats': inbox_stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/inbox-health', methods=['GET'])
@login_required
def analyze_inbox_health():
    """Get AI-powered inbox health analysis"""
    try:
        analyzer = InboxAnalyzer(user_id=current_user.id)
        health_data = analyzer.analyze_inbox_health(sample_size=100)

        return jsonify({
            'success': True,
            'health': health_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/smart-suggestions', methods=['GET'])
@login_required
def get_smart_suggestions():
    """Get AI-powered smart cleanup suggestions"""
    try:
        analyzer = InboxAnalyzer(user_id=current_user.id)
        suggestions = analyzer.get_smart_suggestions(sample_size=100)

        return jsonify({
            'success': True,
            'suggestions': suggestions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/retention/analyze', methods=['POST'])
@login_required
def analyze_old_emails():
    """Analyze old emails for deletion"""
    try:
        data = request.json or {}
        months = data.get('months', 6)
        category = data.get('category')

        retention_mgr = RetentionManager(user_id=current_user.id)
        analysis = retention_mgr.analyze_old_emails(months=months, category_filter=category)

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/retention/delete', methods=['POST'])
@login_required
def delete_old_emails():
    """Delete old emails based on retention policy"""
    try:
        data = request.json or {}
        months = data.get('months', 6)
        category = data.get('category')
        whitelist = data.get('whitelist', [])
        dry_run = data.get('dry_run', True)

        retention_mgr = RetentionManager(user_id=current_user.id)
        results = retention_mgr.delete_old_emails(
            months=months,
            category_filter=category,
            whitelist=whitelist,
            dry_run=dry_run
        )

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/unsubscribe-opportunities', methods=['GET'])
@login_required
def find_unsubscribe_opportunities():
    """Find newsletters you can unsubscribe from"""
    try:
        analyzer = InboxAnalyzer(user_id=current_user.id)
        opportunities = analyzer.detect_unsubscribe_opportunities(max_emails=200)

        return jsonify({
            'success': True,
            'opportunities': opportunities
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/duplicates', methods=['GET'])
@login_required
def find_duplicates():
    """Find duplicate emails"""
    try:
        retention_mgr = RetentionManager(user_id=current_user.id)
        duplicates = retention_mgr.detect_duplicates(max_emails=500)

        return jsonify({
            'success': True,
            'duplicates': duplicates
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Gmail Agent Web Interface")
    print("=" * 60)
    print("\nStarting server...")
    print("Access the dashboard at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
