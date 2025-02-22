import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
from utils import (
    load_study_data, save_study_data, format_time,
    get_subject_stats, get_daily_quote
)

# Page config
st.set_page_config(
    page_title="Study Tracker",
    page_icon="⏱️",
    layout="wide"
)

# Load custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = None
if 'pomodoro_duration' not in st.session_state:
    st.session_state.pomodoro_duration = 25  # Default 25 minutes
if 'current_streak' not in st.session_state:
    st.session_state.current_streak = 0
if 'last_study_date' not in st.session_state:
    st.session_state.last_study_date = None
if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False
if 'subjects' not in st.session_state:
    st.session_state.subjects = ["Physics", "Chemistry", "Biology", "Math"]
if 'manual_time' not in st.session_state:
    st.session_state.manual_time = 0

# Calculate streak
def update_streak():
    today = datetime.now().date()
    if st.session_state.last_study_date:
        last_date = datetime.strptime(st.session_state.last_study_date, '%Y-%m-%d').date()
        if today - last_date == timedelta(days=1):
            st.session_state.current_streak += 1
        elif today - last_date > timedelta(days=1):
            st.session_state.current_streak = 1
    st.session_state.last_study_date = today.strftime('%Y-%m-%d')

# Center container
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Daily quote
    st.markdown(f'<div class="quote">"{get_daily_quote()}"</div>', unsafe_allow_html=True)

    # Settings toggle
    if st.button("⚙️ Settings", key="settings_toggle"):
        st.session_state.show_settings = not st.session_state.show_settings

    # Settings panel
    if st.session_state.show_settings:
        with st.expander("⚙️ Timer Settings", expanded=True):
            st.session_state.pomodoro_duration = st.slider(
                "Pomodoro Duration (minutes)",
                min_value=1,
                max_value=60,
                value=st.session_state.pomodoro_duration
            )

            # Subject management
            st.markdown("### 📚 Subject Management")
            new_subject = st.text_input("Add New Subject", key="new_subject").strip()
            if new_subject and st.button("Add Subject"):
                if new_subject not in st.session_state.subjects:
                    st.session_state.subjects.append(new_subject)
                    st.success(f"Added {new_subject} to subjects!")
                    st.rerun()
                else:
                    st.warning("Subject already exists!")

            # Delete subjects
            if st.session_state.subjects:
                subject_to_delete = st.selectbox(
                    "Remove Subject",
                    st.session_state.subjects,
                    key="delete_subject"
                )
                if st.button("Delete Subject"):
                    st.session_state.subjects.remove(subject_to_delete)
                    st.success(f"Removed {subject_to_delete} from subjects!")
                    st.rerun()

            # Manual time adjustment
            if st.session_state.timer_running:
                st.markdown("### ⚡ Quick Time Adjustment")
                st.session_state.manual_time = st.number_input(
                    "Adjust elapsed time (minutes)",
                    min_value=0,
                    value=int((time.time() - st.session_state.start_time) / 60),
                    step=1
                )
                if st.button("Update Time"):
                    st.session_state.start_time = time.time() - (st.session_state.manual_time * 60)
                    st.success("Timer adjusted!")
                    st.rerun()

    # Load total study time
    study_data = load_study_data()
    total_time, _ = get_subject_stats(study_data)

    # Display total study time
    st.markdown(f'<div class="total-time">Total Study Time: {format_time(total_time)}</div>', unsafe_allow_html=True)

    # Clock SVG with progress
    progress = 0
    if st.session_state.timer_running:
        elapsed = int(time.time() - st.session_state.start_time)
        progress = min(1, elapsed / (st.session_state.pomodoro_duration * 60))

    svg_class = "timer-running" if st.session_state.timer_running else ""
    progress_offset = 283 * (1 - progress)

    clock_svg = f'''
    <div class="clock-container {svg_class}">
        <svg viewBox="0 0 100 100">
            <circle class="clock-face" cx="50" cy="50" r="45" />
            <circle class="progress-ring" cx="50" cy="50" r="45" 
                    stroke-dasharray="283" stroke-dashoffset="{progress_offset}" />
            <line class="clock-hand" x1="50" y1="50" x2="50" y2="15" />
        </svg>
    </div>
    '''
    st.markdown(clock_svg, unsafe_allow_html=True)

    # Timer display
    if st.session_state.timer_running:
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = (st.session_state.pomodoro_duration * 60) - elapsed
        if remaining <= 0:
            st.session_state.timer_running = False
            st.balloons()
            update_streak()
            st.markdown('<div class="completion-message">🎉 Great job! Take a break!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="timer-display">{format_time(remaining)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="timer-display">{format_time(st.session_state.pomodoro_duration * 60)}</div>', unsafe_allow_html=True)

    # Streak display
    if st.session_state.current_streak > 0:
        st.markdown(f'<div class="streak-badge">🔥 {st.session_state.current_streak} Day Streak!</div>', unsafe_allow_html=True)

    # Subject selection
    st.markdown('<div class="subject-container">', unsafe_allow_html=True)
    for subject in st.session_state.subjects:
        if st.button(
            subject,
            key=f"subject_{subject}",
            use_container_width=True,
            help=f"Click to start studying {subject}"
        ):
            st.session_state.selected_subject = subject
            if not st.session_state.timer_running:
                st.session_state.timer_running = True
                st.session_state.start_time = time.time()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Timer controls
    if st.session_state.timer_running:
        if st.button("Stop", use_container_width=True):
            duration = int(time.time() - st.session_state.start_time)

            # Save session data
            study_data = load_study_data()
            study_data.append({
                "subject": st.session_state.selected_subject,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
            save_study_data(study_data)
            update_streak()

            # Reset timer
            st.session_state.timer_running = False
            st.session_state.start_time = None
            st.session_state.elapsed_time = 0
            st.rerun()

def format_duration_hours(seconds):
    return f"{seconds / 3600:.1f}h"

# Statistics section (collapsed by default)
with st.expander("📊 Study Statistics"):
    study_data = load_study_data()

    if study_data:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(study_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['duration_hours'] = df['duration'] / 3600
        df['date'] = df['timestamp'].dt.date

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        total_time, avg_time = get_subject_stats(study_data)

        col1.metric("Total Study Time", format_time(total_time))
        col2.metric("Average Session", format_time(avg_time))
        col3.metric("Total Sessions", len(study_data))

        # Time periods
        st.markdown("### ⏰ Time Periods")
        period = st.radio(
            "Select Time Period",
            ["Daily", "Weekly", "Lifetime"],
            horizontal=True
        )

        if period == "Daily":
            today = datetime.now().date()
            daily_data = df[df['date'] == today]

            if not daily_data.empty:
                st.markdown(f"#### Today's Progress")
                daily_total = daily_data['duration'].sum()
                st.markdown(f"**Total:** {format_time(daily_total)}")

                # Daily subject breakdown
                fig = px.pie(
                    daily_data,
                    values='duration_hours',
                    names='subject',
                    title="Today's Study Distribution",
                    color_discrete_sequence=['#262730', '#404040', '#606060', '#808080']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No study sessions recorded today. Time to start studying! 📚")

        elif period == "Weekly":
            # Last 7 days analysis
            last_week = datetime.now().date() - timedelta(days=7)
            weekly_data = df[df['date'] > last_week]

            if not weekly_data.empty:
                # Daily totals for the week
                daily_totals = weekly_data.groupby('date')['duration_hours'].sum().reset_index()

                fig = px.bar(
                    daily_totals,
                    x='date',
                    y='duration_hours',
                    title="Last 7 Days Study Time",
                    color_discrete_sequence=['#404040']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis_title="Date",
                    yaxis_title="Hours"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Weekly subject distribution
                st.markdown("#### Subject Distribution")
                fig = px.pie(
                    weekly_data,
                    values='duration_hours',
                    names='subject',
                    color_discrete_sequence=['#262730', '#404040', '#606060', '#808080']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No study sessions recorded in the last week. Let's change that! 📚")

        else:  # Lifetime
            if not df.empty:
                # Monthly trend
                monthly_data = df.groupby([df['timestamp'].dt.to_period('M')])['duration_hours'].sum().reset_index()
                monthly_data['timestamp'] = monthly_data['timestamp'].astype(str)

                fig = px.line(
                    monthly_data,
                    x='timestamp',
                    y='duration_hours',
                    title="Study Time Trend",
                    color_discrete_sequence=['#404040']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis_title="Month",
                    yaxis_title="Hours"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Subject distribution
                st.markdown("#### Overall Subject Distribution")
                fig = px.pie(
                    df,
                    values='duration_hours',
                    names='subject',
                    color_discrete_sequence=['#262730', '#404040', '#606060', '#808080']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)

                # Top statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 🏆 Most Studied Subject")
                    top_subject = df.groupby('subject')['duration'].sum().idxmax()
                    top_subject_time = df[df['subject'] == top_subject]['duration'].sum()
                    st.markdown(f"**{top_subject}** ({format_time(top_subject_time)})")

                with col2:
                    st.markdown("#### ⭐ Longest Session")
                    longest_session = df['duration'].max()
                    longest_subject = df[df['duration'] == longest_session]['subject'].iloc[0]
                    st.markdown(f"**{format_time(longest_session)}** ({longest_subject})")
            else:
                st.info("No study sessions recorded yet. Time to start your study journey! 📚")
    else:
        st.info("Start your first study session to see statistics!")