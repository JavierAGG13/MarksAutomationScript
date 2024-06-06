import csv
import re

# path to files 
xytech_file_path = 'C:\\Users\\yungj\\OneDrive\\Desktop\\467 CHAJA\\Project1467\\Xytech.txt'
baselight_file_path = 'C:\\Users\\yungj\\OneDrive\\Desktop\\467 CHAJA\\Project1467\\Baselight_export.txt'

# Initialize variables to hold the extracted information
producer = operator = job = notes = ""
locations = []

hpsans_mapping = {
    'VFX/Hydraulx': '/hpsans12/production',
    'VFX/Framestore': '/hpsans13/production',
    'VFX/AnimalLogic': '/hpsans14/production',
    'shot_1ab': '/hpsans15/production',
    'shot_2b': '/hpsans11/production',
    'partC': '/hpsans17/production',
    # Add other mappings as required
}


# Function to parse the Xytech file
def parse_xytech(file_path):
    global producer, operator, job, notes
    with open(file_path, 'r') as file:
        content = file.read()
        producer = re.search(r"Producer:\s*(.+)", content).group(1)
        operator = re.search(r"Operator:\s*(.+)", content).group(1)
        job = re.search(r"Job:\s*(.+)", content).group(1)
        notes = re.search(r"Notes:\s*(.+)", content, re.DOTALL).group(1).strip()

def parse_baselight(file_path):
    frame_data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        # Skip empty lines or lines that do not contain expected path data
        if not line.strip() or '/baselightfilesystem1' not in line:
            continue
        # Perform the path replacement
        path = line.strip()
        for key, value in hpsans_mapping.items():
            if key in path:
                path = path.replace('/baselightfilesystem1', value)
                break
        else: # If none of the keys are in the path, use the default replacement
            path = path.replace('/baselightfilesystem1', '/hpsans13/production')

        # Split the path and frames and sort them
        path, *frames = path.split()
        frames = sorted(int(frame) for frame in frames if frame not in ['<null>', '<err>'])

        # Organize into individual frames and ranges
        organized_frames = organize_into_ranges(frames)
        
        # Append the organized frames with the path
        frame_data.append([path, organized_frames])
    return frame_data

# function to organize frames into ranges
def organize_into_ranges(frames):
    if not frames:
        return ""
    ranges = []
    start = end = frames[0]
    for frame in frames[1:]:
        if frame == end + 1:
            end = frame
        else:
            ranges.append(f"{start}-{end}" if start != end else str(start))
            start = end = frame
    ranges.append(f"{start}-{end}" if start != end else str(start))
    return ", ".join(ranges)

# Parse the files
parse_xytech(xytech_file_path)
locations = parse_baselight(baselight_file_path)

# Export the information to a CSV file
csv_file = 'C:\\Users\\yungj\\OneDrive\\Desktop\\467 CHAJA\\Project1467\\extracted_info.csv'
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Producer', 'Operator', 'Job', 'Notes'])
    writer.writerow([producer, operator, job, notes.replace('\n', '; ')])
    writer.writerow([])  # Empty row for spacing
    writer.writerow(['Location', 'Frames to Fix'])  # Headers for the following data
    
    # Write location and frames data, each frame range in a new row
    for location, frame_ranges in locations:
        # Each frame range is separated by a comma in the frame_ranges string
        for frame_range in frame_ranges.split(', '):
            writer.writerow([location, frame_range])
    
    
print(f"Information exported to {csv_file} successfully.")
