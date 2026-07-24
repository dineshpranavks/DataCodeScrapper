from flask import Blueprint, render_template, request, jsonify, send_file
import os
from pathlib import Path
from dashboard.database import get_statistics, get_problems, get_problem, get_distinct_values

bp = Blueprint('main', __name__)

# --- View Routes ---

@bp.route('/')
def index():
    stats = get_statistics()
    return render_template('index.html', stats=stats)

@bp.route('/problems')
def problems():
    topics = get_distinct_values("topic")
    difficulties = get_distinct_values("difficulty")
    contests = get_distinct_values("contest_id")
    return render_template('problems.html', topics=topics, difficulties=difficulties, contests=contests)

@bp.route('/statistics')
def statistics():
    return render_template('statistics.html')

@bp.route('/problem/<problem_id>')
def problem_detail(problem_id):
    problem = get_problem(problem_id)
    if not problem:
        from flask import abort
        abort(404)
        
    # Check if XML exists
    xml_path = Path(f"dataset/xml/{problem_id}.xml").resolve()
    has_xml = xml_path.exists()
    
    return render_template('problem.html', problem=problem, has_xml=has_xml)

@bp.route('/about')
def about():
    # Simple about page or redirect to home for now, as no specific about page requirements were given 
    # except it exists in the nav bar.
    return render_template('index.html', stats=get_statistics())

# --- API Routes ---

@bp.route('/api/problems')
def api_problems():
    limit = int(request.args.get('limit', 25))
    offset = int(request.args.get('offset', 0))
    search = request.args.get('search', '')
    topic = request.args.get('topic', '')
    difficulty = request.args.get('difficulty', '')
    contest_id = request.args.get('contest_id', '')
    sort_by = request.args.get('sort_by', 'problem_id')
    sort_order = request.args.get('sort_order', 'ASC')
    
    result = get_problems(limit, offset, search, topic, difficulty, contest_id, sort_by, sort_order)
    return jsonify(result)

@bp.route('/api/problem/<problem_id>')
def api_problem(problem_id):
    problem = get_problem(problem_id)
    if problem:
        return jsonify(problem)
    return jsonify({"error": "Not found"}), 404

@bp.route('/api/statistics')
def api_statistics():
    return jsonify(get_statistics())

@bp.route('/api/topics')
def api_topics():
    return jsonify(get_distinct_values("topic"))

@bp.route('/api/difficulties')
def api_difficulties():
    return jsonify(get_distinct_values("difficulty"))

# --- File Download Route ---

@bp.route('/download/xml/<problem_id>')
def download_xml(problem_id):
    project_root = Path(__file__).resolve().parent.parent
    xml_path = project_root / "dataset" / "xml" / f"{problem_id}.xml"
    
    if xml_path.exists():
        return send_file(xml_path, as_attachment=True)
    
    from flask import abort
    abort(404)
