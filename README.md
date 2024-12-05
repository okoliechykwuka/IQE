# learn-content_eval-app


### System Components:
a. File Processing Layer
   - PDF Processor (PyPDF2/pdf2image)
   - Video Processor (yt-dlp + Langchain YouTube loader)
   - Audio Processor (OpenAI Whisper)

b. Content Analysis Layer
   - Content chunking (LangChain text splitters)
   - Quality assessment (OpenAI GPT-4)
   - Scoring engine

c. UI Layer (Streamlit)
   - File upload
   - Progress tracking
   - Interactive steps
   - Results display

### Evaluation Process Steps:

Step 1: Content Intake & Validation
- Accept file uploads (PDF/Video/Audio)
- Validate file formats
- Process content for analysis

Step 2: Scope Confirmation
- Generate content summary
- Display key topics/sections
- Get user confirmation

Step 3: Evaluation Depth Selection
- Present depth options:
  * Quick Review (1-2 criteria)
  * Standard Review (3-4 criteria)
  * Comprehensive Review (all criteria)

Step 4: Preliminary Review
- Apply selected evaluation methods
- Generate initial insights
- Show progress indicators

Step 5: Detailed Analysis
- Apply additional evaluation methods
- Generate detailed scoring
- Compile recommendations

Step 6: Final Output
- Generate numerical scores (0-10)
- Create written summary
- Provide downloadable report

### Quality Assessment Criteria:
1. Learning Objectives (0-10)
   - Clarity
   - Measurability
   - Alignment

2. Content Structure (0-10)
   - Organization
   - Flow
   - Coherence

3. Engagement Elements (0-10)
   - Interactivity
   - Multimedia usage
   - Practice opportunities

4. Assessment Design (0-10)
   - Variety of methods
   - Feedback mechanisms
   - Knowledge validation




##### How to run the app
```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```


The app is launched to listen to the port 8501 at your localhost
```plain
http:localhost:8501
```

Follow the chat instruction to evaluate your course content.
Currently it is only able to process the text contents