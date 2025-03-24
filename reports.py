import sqlite3
import plotly.graph_objects as go
import plotly.io as pio


# def fetch_task_data(user_id):
#     # Connect to the database
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()

#     # Query to fetch task statuses for the given user
#     query = """
#     SELECT status, COUNT(*) 
#     FROM tasks 
#     WHERE user.id = ? 
#     GROUP BY status
#     """
#     cursor.execute(query, (current_user.id,))
#     data = cursor.fetchall()

#     conn.close()
#     return data

# def generate_progress_pie_chart(user_id):
#     task_data = fetch_task_data(user_id)

#     labels = [row[0] for row in task_data]  # Task categories
#     values = [row[1] for row in task_data]  # Task count per category

#     fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
#     fig.update_layout(title_text="Task Distribution by Category")

#     # Convert figure to an HTML div
#     chart_html = pio.to_html(fig, full_html=False)

#     return chart_html  # Return HTML instead of displaying

def fetch_task_data(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    query = """
    SELECT status, COUNT(*) 
    FROM tasks 
    WHERE assignedTo = ? 
    GROUP BY status
    """
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    
    conn.close()
    return data

def generate_progress_pie_chart(user_id):
    task_data = fetch_task_data(user_id)

    labels = [row[0] for row in task_data]  # Task statuses ###FIX: Change to 'status' instead of 'category'
    values = [row[1] for row in task_data]  # Task count per category

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_layout(title_text="Task Distribution by Status")

    chart_html = pio.to_html(fig, full_html=False)

    return chart_html  # Return HTML instead of displaying
