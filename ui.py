import gradio as gr
import sqlite3
import pandas as pd

def run_query(query):
    try:
        conn = sqlite3.connect("unr_schedule.db")
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return str(e)

q = """
SELECT Course, [Class Nbr], Section, [Days & Times], Room, Instructor, [Meeting Dates], [Class Stat]
FROM [Class Search]
WHERE {};
"""

def query_spring():
    return run_query(q.format("Term = 1"))

def query_lower_div():
    return run_query(q.format("Catalog < 300"))

def query_cs_135():
    return run_query(q.format("Course = 'CS 135'"))

def query_upper_div_cs():
    return run_query(q.format("Catalog >= 300"))

def query_keith_hastings():
    return run_query(q.format("Course LIKE 'CS%' AND (Instructor LIKE '%Keith%' OR Instructor LIKE '%Hastings%')"))

with gr.Blocks() as demo:
    gr.Markdown("## UNR Class Search")

    with gr.Row():
        b1 = gr.Button("All Spring Courses")
        b2 = gr.Button("Lower Division CS")
        b3 = gr.Button("All CS 135 Sections")

    with gr.Row():
        b4 = gr.Button("Upper Division CS")
        b5 = gr.Button("Courses by Keith or Hastings")

    with gr.Column():
        output = gr.Dataframe(max_height=900)

    b1.click(fn=query_spring, outputs=output)
    b2.click(fn=query_lower_div, outputs=output)
    b3.click(fn=query_cs_135, outputs=output)
    b4.click(fn=query_upper_div_cs, outputs=output)
    b5.click(fn=query_keith_hastings, outputs=output)

demo.launch()
