# Spec and build

## Configuration
- **Artifacts Path**: {@artifacts_path} → `.zenflow/tasks/{task_id}`

---

## Agent Instructions

Ask the user questions when anything is unclear or needs their input. This includes:
- Ambiguous or incomplete requirements
- Technical decisions that affect architecture or user experience
- Trade-offs that require business context

Do not make assumptions on important decisions — get clarification first.

---

## Workflow Steps

### [x] Step: Technical Specification
<!-- chat-id: 965a5b59-7a5c-4ae9-9636-6ad3ce9ae79b -->

**Difficulty**: Hard - Complex architectural transformation from physical to online meetings

**Completed**:
- ✅ Technical specification created in `spec.md`
- ✅ Detailed implementation plan created in `implementation-plan.md`
- ✅ Identified 12 concrete implementation tasks
- ✅ Defined data model, API, and UI changes
- ✅ Established verification criteria

See `spec.md` for full technical details and `implementation-plan.md` for detailed task breakdown.

---

## Implementation Tasks

### [x] Task 1: Setup & Configuration
<!-- chat-id: d2b3661f-6ecd-4db5-902f-ba654f2f51dc -->
Configure platform API credentials (Zoom, Deepgram/AssemblyAI) and update backend configuration.

**Files**: `backend/config.py`, `backend/.env.example`

---

### [x] Task 2: Backend Data Models Update
<!-- chat-id: c6506e62-9afc-4aa4-aa19-a8c76eeb7e42 -->
Modify storage models for online meetings, word-level timestamps, and structured summaries.

**Files**: `backend/storage.py`

---

### [ ] Task 3: Platform Integration Base
Create abstract base class for platform integrations.

**Files**: `backend/platform_integrations/base_platform.py` (new)

---

### [ ] Task 4: Zoom Integration
Implement Zoom OAuth flow, meeting details retrieval, and recording download.

**Files**: `backend/platform_integrations/zoom_integration.py` (new), `backend/app.py`

---

### [ ] Task 5: Enhanced Transcription with Timestamps
Integrate Deepgram or AssemblyAI for word-level timestamp transcription.

**Files**: `backend/word_timestamp_transcriber.py` (new), `backend/transcriber.py`

---

### [ ] Task 6: Structured Summary Generation
Enhance summarizer to generate Overview, Action Items, and Outline sections.

**Files**: `backend/summarizer.py`, `backend/app.py`

---

### [ ] Task 7: Audio Player Component
Create React audio player component with playback controls and sync hooks.

**Files**: `frontend/src/components/AudioPlayer.js` (new), `frontend/src/hooks/useAudioSync.js` (new)

---

### [ ] Task 8: Synchronized Transcript Component
Create transcript component with real-time highlighting and click-to-seek.

**Files**: `frontend/src/components/SyncedTranscript.js` (new), `frontend/src/utils/transcriptHighlighter.js` (new)

---

### [ ] Task 9: Structured Summary View
Create summary component with Overview, Action Items, and Outline sections.

**Files**: `frontend/src/components/StructuredSummary.js` (new), `frontend/src/components/ActionItemsList.js` (new), `frontend/src/components/MeetingOutline.js` (new)

---

### [ ] Task 10: Update Meeting Creation Flow
Add platform selection and file upload to meeting creation.

**Files**: `frontend/src/pages/CreateMeeting.js`

---

### [ ] Task 11: Meeting Detail Redesign
Complete overhaul with audio player, synced transcript, and structured summary (Otter AI-like layout).

**Files**: `frontend/src/pages/MeetingDetail.js`, `frontend/src/pages/MeetingDetail.css`

---

### [ ] Task 12: Testing & Refinement
End-to-end testing, bug fixes, performance optimization, and polish.

**Activities**: Upload flow, Zoom flow, playback sync, summary validation, edge cases

---

### [ ] Step: Final Report

After completing all implementation tasks, write a comprehensive report to `{@artifacts_path}/report.md` describing:
- What was implemented
- How the solution was tested
- Key challenges and solutions
- Known limitations
- Future enhancements
