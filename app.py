from flask import Flask, render_template, request, send_file, Response
from youtube_comment_downloader import YoutubeCommentDownloader
import pandas as pd
from langdetect import detect
import io

app = Flask(__name__)

# Mapping of language codes to their language names
LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'ur': 'Urdu',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'or': 'Odia',
    'as': 'Assamese',
    'pa': 'Punjabi',
    'sd': 'Sindhi',
    'sanskrit': 'Sanskrit'
}

# Function to detect a specific language
def detect_language(text, lang_code):
    try:
        return detect(text) == lang_code
    except:
        return False

# Route to display the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to process the input and return filtered comments
@app.route('/process', methods=['POST'])
def process_video():
    video_id = request.form['video_id']
    lang_code = request.form['language_code']

    # Initialize the downloader
    downloader = YoutubeCommentDownloader()
    
    # Fetch comments for the given video ID
    comments = downloader.get_comments_from_url(f'https://www.youtube.com/watch?v={video_id}')
    
    # List to hold all comments data
    comments_data = []
    
    # Process each comment and store in the list
    for comment in comments:
        comments_data.append({
            'author': comment.get('author', ''),
            'text': comment.get('text', ''),
            'time': comment.get('time', ''),
            'likes': comment.get('likes', 0)
        })
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(comments_data)
    
    # Filter DataFrame for the selected language
    df_filtered = df[df['text'].apply(lambda text: detect_language(text, lang_code))]
    
    # Save the filtered DataFrame to an in-memory file
    output = io.BytesIO()
    df_filtered.to_csv(output, index=False)
    output.seek(0)
    
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': f'attachment;filename=comments_{LANGUAGES.get(lang_code, "unknown_language")}.csv'})

if __name__ == '__main__':
    app.run(debug=True)
