import streamlit as st
import re
from datetime import datetime, timedelta

def extract_events(events_text):
    """
    Extracts stoppage events from the input text.
    Looks for patterns like "45+3" (45 minutes plus 3 added time) or specific timestamps.
    """
    events = []
    lines = events_text.strip().split('\n')
    
    time_pattern = re.compile(r'(\d+)[\':](\d+)[\'\"]?\s+(.+)')
    added_time_pattern = re.compile(r'(\d+)\+(\d+)[\'\"]?\s+(.+)')
    
    for line in lines:
        if not line.strip():
            continue
            
        # Try to find normal time pattern (e.g., 23' Foul)
        time_match = time_pattern.match(line)
        if time_match:
            minute = int(time_match.group(1))
            second = int(time_match.group(2)) if time_match.group(2) else 0
            description = time_match.group(3)
            events.append((minute, second, description))
            continue
            
        # Try to find added time pattern (e.g., 45+3' Foul)
        added_time_match = added_time_pattern.match(line)
        if added_time_match:
            base_minute = int(added_time_match.group(1))
            added_minutes = int(added_time_match.group(2))
            minute = base_minute + added_minutes
            description = added_time_match.group(3)
            events.append((minute, 0, description))
            continue
            
        # If no specific pattern found, try to extract any number at the beginning
        numbers = re.findall(r'^\s*(\d+)', line)
        if numbers:
            minute = int(numbers[0])
            description = re.sub(r'^\s*\d+\s*', '', line)
            events.append((minute, 0, description))
    
    return events

def calculate_stoppages(events):
    """
    Calculates the total stoppage time based on extracted events.
    Identifies stoppage and resumption events to calculate duration.
    """
    # Keywords indicating stoppage in English
    stoppage_keywords = ['stoppage', 'stopped', 'pause', 'interrupted', 
                        'foul', 'injury', 'treatment', 'var', 'review',
                        'card', 'substitution', 'drinks break', 'water break',
                        'offside', 'delay', 'medical', 'check', 'yellow', 'red',
                        'cooling break', 'goal check', 'penalty', 'corner']
    
    # Keywords indicating resumption of play in English
    resumption_keywords = ['resumption', 'resumes', 'restarts', 'ball in play',
                          'play continues', 'game continues', 'back underway',
                          'play on', 'restart', 'play resumes', 'match resumes']
    
    first_half_stoppages = []
    second_half_stoppages = []
    
    stoppage_start = None
    
    for i, event in enumerate(events):
        minute, second, description = event
        description = description.lower()
        
        # Check if it's a stoppage event
        if any(keyword in description for keyword in stoppage_keywords) and stoppage_start is None:
            stoppage_start = (minute, second)
        
        # Check if it's a resumption event after a stoppage
        elif any(keyword in description for keyword in resumption_keywords) and stoppage_start is not None:
            duration_minutes = minute - stoppage_start[0]
            duration_seconds = second - stoppage_start[1]
            
            # Adjust if seconds are negative
            if duration_seconds < 0:
                duration_minutes -= 1
                duration_seconds += 60
            
            # Record the stoppage in the appropriate half
            if stoppage_start[0] <= 45:
                first_half_stoppages.append((duration_minutes, duration_seconds))
            else:
                second_half_stoppages.append((duration_minutes, duration_seconds))
            
            stoppage_start = None
    
    # Calculate total stoppage time
    first_half_time = sum(m * 60 + s for m, s in first_half_stoppages)
    second_half_time = sum(m * 60 + s for m, s in second_half_stoppages)
    
    return first_half_time, second_half_time, first_half_stoppages, second_half_stoppages

def format_time(seconds):
    """Formats time in seconds to minutes and seconds."""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes} min and {remaining_seconds} sec"

def main():
    st.title("Match Stoppage Time Calculator")
    
    st.markdown("""
    ## Instructions
    1. Paste the match events in the field below
    2. Recommended format: `minute' event description` (e.g., `23' Foul by Smith`)
    3. Other accepted formats: `45+2' Yellow card` or `78:30 Substitution`
    4. For better accuracy, include both start and end events for each stoppage
    """)
    
    # Example input
    example = """5' Foul by Johnson at the edge of the box
7' Play resumes after free kick
23' VAR reviewing possible penalty
25' Game restarts after VAR review
42' Medical treatment for injured player
45' Match resumes
52' Substitution for away team
53' Ball back in play
67' Drinks break
70' Play continues after drinks break
85' Red card for harsh tackle
87' Game restarts"""
    
    # Field for event input
    events_text = st.text_area("Paste match events below:", 
                              height=300, 
                              placeholder=example)
    
    if st.button("Calculate Stoppage Time"):
        if events_text:
            events = extract_events(events_text)
            
            if events:
                # Display extracted events for verification
                st.subheader("Identified Events:")
                for minute, second, description in events:
                    formatted_time = f"{minute}:{second:02d}" if second > 0 else f"{minute}'"
                    st.write(f"{formatted_time} - {description}")
                
                # Calculate and display stoppage time
                first_half_time, second_half_time, first_half_stoppages, second_half_stoppages = calculate_stoppages(events)
                
                st.subheader("Stoppage Summary")
                
                # First half
                st.markdown("### First Half")
                if first_half_stoppages:
                    for i, (minutes, seconds) in enumerate(first_half_stoppages, 1):
                        st.write(f"Stoppage {i}: {minutes} min and {seconds} sec")
                    st.success(f"Total first half stoppage time: {format_time(first_half_time)}")
                else:
                    st.info("No stoppages identified in the first half.")
                
                # Second half
                st.markdown("### Second Half")
                if second_half_stoppages:
                    for i, (minutes, seconds) in enumerate(second_half_stoppages, 1):
                        st.write(f"Stoppage {i}: {minutes} min and {seconds} sec")
                    st.success(f"Total second half stoppage time: {format_time(second_half_time)}")
                else:
                    st.info("No stoppages identified in the second half.")
                
                # Overall total
                total_time = first_half_time + second_half_time
                st.subheader(f"Total match stoppage time: {format_time(total_time)}")
            else:
                st.error("Could not identify events in the correct format. Please check the format of the events entered.")
        else:
            st.warning("Please enter match events to calculate stoppage time.")

if __name__ == "__main__":
    main()
