import json

categories = [
    "Chat Interface", "Artifacts", "Conversation Management", "Projects", 
    "Model Selection", "Custom Instructions", "Settings", "Advanced Features",
    "Collaboration", "Search & Discovery", "Usage Tracking", "Onboarding",
    "Accessibility", "Responsive Design", "API & Backend", "Database"
]

test_cases = []

# Chat Interface (20 tests)
for i in range(1, 21):
    test_cases.append({
        "category": "Chat Interface",
        "description": f"Verify chat functionality case {i}",
        "steps": ["Open chat", f"Perform action {i}", "Verify output"],
        "passes": False
    })

# Specific detailed tests to replace generics where possible
detailed_tests = [
    # Chat Interface
    ("Chat Interface", "Verify clean, centered chat layout with message bubbles", ["Open application", "Check chat area alignment", "Verify user message style", "Verify assistant message style"]),
    ("Chat Interface", "Verify streaming message responses", ["Send a message", "Observe typing indicator", "Verify text appears incrementally"]),
    ("Chat Interface", "Verify markdown rendering", ["Send message with bold, italic, and lists", "Verify proper formatting in response"]),
    ("Chat Interface", "Verify code blocks with syntax highlighting", ["Request code snippet", "Verify distinct background", "Check syntax highlighting colors"]),
    ("Chat Interface", "Verify code block copy button", ["Hover over code block", "Click copy button", "Paste to verify content"]),
    ("Chat Interface", "Verify LaTeX/math equation rendering", ["Request math equation", "Verify proper rendering"]),
    ("Chat Interface", "Verify image upload in messages", ["Click attachment button", "Select image", "Verify image preview in chat"]),
    ("Chat Interface", "Verify multi-turn conversations", ["Send message", "Get response", "Send follow-up", "Verify context is maintained"]),
    ("Chat Interface", "Verify message editing", ["Hover over user message", "Click edit", "Change text and save", "Verify new response generated"]),
    ("Chat Interface", "Verify stop generation button", ["Send long prompt", "Click stop generating", "Verify stream stops immediately"]),
    ("Chat Interface", "Verify auto-resize textarea", ["Type long multi-line message", "Verify input box grows"]),
    ("Chat Interface", "Verify character count display", ["Type text", "Check character count updates"]),
    ("Chat Interface", "Verify token estimation", ["Type text", "Check estimated tokens update"]),
    ("Chat Interface", "Verify Enter to send", ["Type message", "Press Enter", "Verify message sent"]),
    ("Chat Interface", "Verify Shift+Enter for newline", ["Type line 1", "Press Shift+Enter", "Type line 2", "Verify newline created"]),
    ("Chat Interface", "Verify empty message handling", ["Focus input", "Press Enter without text", "Verify no message sent"]),
    ("Chat Interface", "Verify very long message handling", ["Paste large text", "Send message", "Verify handling without crash"]),
    ("Chat Interface", "Verify scroll to bottom on new message", ["Be at top of history", "Send message", "Verify auto-scroll to bottom"]),
    ("Chat Interface", "Verify user avatar display", ["Check user message", "Verify user avatar/initials"]),
    ("Chat Interface", "Verify assistant avatar display", ["Check assistant message", "Verify Claude icon"]),

    # Artifacts (20 tests)
    ("Artifacts", "Verify artifact detection", ["Ask for code", "Verify artifact panel opens"]),
    ("Artifacts", "Verify artifact side panel rendering", ["Trigger artifact", "Check side panel animation"]),
    ("Artifacts", "Verify code artifact viewer", ["Generate code artifact", "Check syntax highlighting in panel"]),
    ("Artifacts", "Verify HTML preview", ["Generate HTML artifact", "Click preview tab", "Verify rendered HTML"]),
    ("Artifacts", "Verify SVG preview", ["Generate SVG artifact", "Verify SVG graphic renders"]),
    ("Artifacts", "Verify React component preview", ["Generate React artifact", "Verify component interacts"]),
    ("Artifacts", "Verify Mermaid diagram rendering", ["Generate Mermaid graph", "Verify diagram renders correctly"]),
    ("Artifacts", "Verify text document artifacts", ["Generate markdown doc", "Verify clean text view"]),
    ("Artifacts", "Verify mixed content artifacts", ["Generate artifact with CSS and JS", "Verify correct isolation/rendering"]),
    ("Artifacts", "Verify artifact editing", ["Open artifact", "Edit code", "Verify preview updates"]),
    ("Artifacts", "Verify artifact re-prompting", ["Open artifact", "Click re-prompt", "Send modification request", "Verify update"]),
    ("Artifacts", "Verify full-screen artifact view", ["Click full-screen toggle", "Verify modal view"]),
    ("Artifacts", "Verify close full-screen", ["Click close on full-screen", "Verify return to side panel"]),
    ("Artifacts", "Verify download artifact", ["Click download", "Verify file saved with correct extension"]),
    ("Artifacts", "Verify artifact version navigation", ["Make changes to artifact", "Check version dropdown", "Switch versions"]),
    ("Artifacts", "Verify multiple artifacts in one conversation", ["Generate second artifact", "Check tabs/list in side panel"]),
    ("Artifacts", "Verify closing artifact panel", ["Click close button", "Verify panel collapses"]),
    ("Artifacts", "Verify reopening artifact panel", ["Click artifact in chat history", "Verify panel re-opens"]),
    ("Artifacts", "Verify artifact persistence", ["Reload page", "Check artifacts still accessible"]),
    ("Artifacts", "Verify copy artifact code", ["Click copy in artifact view", "Verify clipboard content"]),

    # Conversation Management (20 tests)
    ("Conversation Management", "Verify create new conversation", ["Click New Chat", "Verify empty state"]),
    ("Conversation Management", "Verify conversation list display", ["Open sidebar", "Check list of chats"]),
    ("Conversation Management", "Verify auto-titling", ["Send first message", "Verify conversation gets meaningful title"]),
    ("Conversation Management", "Verify rename conversation", ["Click title", "Edit text", "Save", "Verify list updates"]),
    ("Conversation Management", "Verify delete conversation", ["Hover conversation", "Click delete", "Confirm", "Verify removed"]),
    ("Conversation Management", "Verify cancel delete", ["Click delete", "Cancel", "Verify not removed"]),
    ("Conversation Management", "Verify search functionality", ["Type in search box", "Verify list filters"]),
    ("Conversation Management", "Verify pin conversation", ["Right-click conversation", "Pin", "Verify moved to top"]),
    ("Conversation Management", "Verify unpin conversation", ["Unpin conversation", "Verify returns to chronological order"]),
    ("Conversation Management", "Verify archive conversation", ["Archive chat", "Verify removed from main list"]),
    ("Conversation Management", "Verify view archived", ["Go to archived view", "Verify chat exists"]),
    ("Conversation Management", "Verify conversation folders creation", ["Create folder", "Verify folder appears"]),
    ("Conversation Management", "Verify move chat to folder", ["Drag chat to folder", "Verify inside folder"]),
    ("Conversation Management", "Verify duplicate conversation", ["Select duplicate", "Verify copy created"]),
    ("Conversation Management", "Verify export JSON", ["Export chat as JSON", "Check formatting"]),
    ("Conversation Management", "Verify export Markdown", ["Export chat as MD", "Check formatting"]),
    ("Conversation Management", "Verify timestamps", ["Check conversation details", "Verify created/updated dates"]),
    ("Conversation Management", "Verify unread indicators", ["Receive message in background", "Check indicator"]),
    ("Conversation Management", "Verify date grouping", ["Check 'Today', 'Yesterday' headers", "Verify sorting"]),
    ("Conversation Management", "Verify long title truncation", ["Create chat with long title", "Verify ellipsis in sidebar"]),

    # Projects (15 tests)
    ("Projects", "Verify create project", ["Click create project", "Enter details", "Verify created"]),
    ("Projects", "Verify project knowledge base upload", ["Upload text file", "Verify recognized"]),
    ("Projects", "Verify project custom instructions", ["Set instructions", "Verify applied to new chats"]),
    ("Projects", "Verify move conversation to project", ["Select chat", "Move to project", "Verify location"]),
    ("Projects", "Verify project switching", ["Switch project context", "Verify sidebar updates"]),
    ("Projects", "Verify project settings", ["Edit project name/desc", "Save", "Verify updates"]),
    ("Projects", "Verify project deletion", ["Delete project", "Verify chats deleted or moved"]),
    ("Projects", "Verify document limits", ["Try to upload too many docs", "Verify warning"]),
    ("Projects", "Verify project analytics", ["Check usage stats", "Verify numbers"]),
    ("Projects", "Verify project search", ["Search within project", "Verify scoped results"]),
    ("Projects", "Verify project templates", ["Create from template", "Verify structure"]),
    ("Projects", "Verify archiving project", ["Archive project", "Verify hidden"]),
    ("Projects", "Verify project color coding", ["Set project color", "Verify UI indicator"]),
    ("Projects", "Verify project sharing (mock)", ["Click share", "Verify UI feedback"]),
    ("Projects", "Verify default project", ["Check default 'General' project exists"]),

    # Model Selection (10 tests)
    ("Model Selection", "Verify default model is Sonnet 4.5", ["Start new chat", "Check capabilities"]),
    ("Model Selection", "Verify switch to Haiku 4.5", ["Select Haiku", "Send message", "Verify response"]),
    ("Model Selection", "Verify switch to Opus 4.1", ["Select Opus", "Send message", "Verify response"]),
    ("Model Selection", "Verify model persistence", ["Switch model", "New chat", "Verify selection persists"]),
    ("Model Selection", "Verify model capabilities display", ["Hover model", "Check info tooltip"]),
    ("Model Selection", "Verify context window indicator", ["Check indicator", "Verify capacity"]),
    ("Model Selection", "Verify switch mid-conversation", ["Send message", "Switch model", "Send next", "Verify works"]),
    ("Model Selection", "Verify model comparison view", ["Open comparison", "Verify layout"]),
    ("Model Selection", "Verify pricing info display", ["Check model details", "Verify pricing text"]),
    ("Model Selection", "Verify model badge in chat", ["Check header", "Verify current model badge"]),

    # Custom Instructions (10 tests)
    ("Custom Instructions", "Verify global custom instructions", ["Set global prompt", "Chat", "Verify influence"]),
    ("Custom Instructions", "Verify project instructions override", ["Set project instructions", "Chat", "Verify priority"]),
    ("Custom Instructions", "Verify instruction templates", ["Load template", "Verify populated"]),
    ("Custom Instructions", "Verify instruction preview", ["Click preview", "Verify effect shown"]),
    ("Custom Instructions", "Verify disable instructions", ["Toggle off", "Chat", "Verify no influence"]),
    ("Custom Instructions", "Verify instruction length limit", ["Enter long text", "Check counter/warning"]),
    ("Custom Instructions", "Verify system prompt injection", ["Check logs/debug", "Verify prompt sent to API"]),
    ("Custom Instructions", "Verify specialized instructions", ["Create coding focus instructions", "Verify code quality"]),
    ("Custom Instructions", "Verify conciseness instructions", ["Create brevity instructions", "Verify short responses"]),
    ("Custom Instructions", "Verify role-play instructions", ["Set pirate persona", "Chat", "Verify style"]),

    # Settings & Preferences (15 tests)
    ("Settings", "Verify light mode", ["Select Light theme", "Verify colors"]),
    ("Settings", "Verify dark mode", ["Select Dark theme", "Verify colors"]),
    ("Settings", "Verify auto theme", ["Select Auto", "Verify matches system"]),
    ("Settings", "Verify font size adjustment", ["Increase font size", "Verify UI scales"]),
    ("Settings", "Verify message density compact", ["Select Compact", "Verify spacing reduces"]),
    ("Settings", "Verify code theme selection", ["Change code theme", "Verify highlight colors"]),
    ("Settings", "Verify language preference", ["Change language", "Verify UI text"]),
    ("Settings", "Verify keyboard shortcuts list", ["Open shortcuts help", "Verify list"]),
    ("Settings", "Verify data export", ["Request export", "Verify download starts"]),
    ("Settings", "Verify API key management", ["View settings", "Verify key hidden/masked"]),
    ("Settings", "Verify clear all chats", ["Click clear all", "Confirm", "Verify empty list"]),
    ("Settings", "Verify reduce motion", ["Toggle reduce motion", "Verify animations disabled"]),
    ("Settings", "Verify privacy toggle", ["Toggle training data", "Verify selection saved"]),
    ("Settings", "Verify account details", ["Check email display", "Verify correct"]),
    ("Settings", "Verify logout", ["Click logout", "Verify returns to login"]),

    # Advanced Features (10 tests)
    ("Advanced Features", "Verify temperature control", ["Adjust slider", "Verify randomness changes"]),
    ("Advanced Features", "Verify max tokens settings", ["Reduce max tokens", "Verify truncation"]),
    ("Advanced Features", "Verify top-p control", ["Adjust top-p", "Verify effect"]),
    ("Advanced Features", "Verify thinking mode", ["Toggle thinking mode", "Verify internal monologue visibility"]),
    ("Advanced Features", "Verify multi-modal input", ["Upload text + image", "Verify understanding"]),
    ("Advanced Features", "Verify voice input mock", ["Click mic", "Verify UI state"]),
    ("Advanced Features", "Verify related prompts", ["Check bottom of response", "Verify suggestions"]),
    ("Advanced Features", "Verify branching", ["Edit middle message", "Verify branch created"]),
    ("Advanced Features", "Verify branch navigation", ["Switch branches", "Verify history updates"]),
    ("Advanced Features", "Verify response suggestions", ["Check input placeholders", "Verify relevance"]),

    # Collaboration (10 tests)
    ("Collaboration", "Verify share link generation", ["Click share", "Verify URL generated"]),
    ("Collaboration", "Verify read-only view", ["Open shared link", "Verify read-only state"]),
    ("Collaboration", "Verify shared artifact view", ["Share artifact", "Verify access"]),
    ("Collaboration", "Verify import from shared", ["Import shared chat", "Verify added to history"]),
    ("Collaboration", "Verify prompt library sharing", ["Share prompt", "Verify accessible"]),
    ("Collaboration", "Verify team workspace mock", ["Switch workspace", "Verify UI change"]),
    ("Collaboration", "Verify export to PDF", ["Export conversation", "Verify PDF format"]),
    ("Collaboration", "Verify template sharing", ["Share project template", "Verify link works"]),
    ("Collaboration", "Verify commenting (mock)", ["Add comment", "Verify visual indicator"]),
    ("Collaboration", "Verify access revocation", ["Delete share link", "Verify link 404s"]),

    # Search & Discovery (10 tests)
    ("Search", "Verify global search", ["Search term", "Verify conversation results"]),
    ("Search", "Verify message search", ["Search specific phrase", "Verify message jump"]),
    ("Search", "Verify artifact search", ["Search code snippet", "Verify artifact found"]),
    ("Search", "Verify filter by date", ["Apply date filter", "Verify results"]),
    ("Search", "Verify filter by model", ["Apply model filter", "Verify results"]),
    ("Search", "Verify command palette open", ["Press Cmd+K", "Verify modal opens"]),
    ("Search", "Verify command palette navigation", ["Use arrows", "Verify selection changes"]),
    ("Search", "Verify command palette action", ["Select 'New Chat'", "Verify action executed"]),
    ("Search", "Verify prompt library search", ["Search prompt", "Verify result"]),
    ("Search", "Verify example conversations", ["Click example", "Verify loaded"]),

    # Usage Tracking (10 tests)
    ("Usage", "Verify token count display", ["Check message footprint", "Verify number"]),
    ("Usage", "Verify cost estimation", ["Check session cost", "Verify calculation"]),
    ("Usage", "Verify daily dashboard", ["Open usage view", "Verify graph"]),
    ("Usage", "Verify monthly dashboard", ["Switch to monthly", "Verify totals"]),
    ("Usage", "Verify limit warning", ["Simulate limit approach", "Verify alert"]),
    ("Usage", "Verify quota tracking", ["Check quota bar", "Verify percentage"]),
    ("Usage", "Verify model usage breakdown", ["Check model stats", "Verify comparison"]),
    ("Usage", "Verify cost per message", ["Inspect message details", "Verify cost displayed"]),
    ("Usage", "Verify export usage report", ["Download report", "Verify CSV"]),
    ("Usage", "Verify currency display", ["Check costs", "Verify symbol/formatting"]),

    # Onboarding (10 tests)
    ("Onboarding", "Verify welcome screen", ["New user load", "Verify welcome visible"]),
    ("Onboarding", "Verify feature tour", ["Start tour", "Verify steps"]),
    ("Onboarding", "Verify example prompts", ["Click example", "Verify input populated"]),
    ("Onboarding", "Verify quick tips", ["Check sidebar tips", "Verify content"]),
    ("Onboarding", "Verify keyboard shortcuts tutorial", ["Start tutorial", "Verify interactive steps"]),
    ("Onboarding", "Verify profile setup", ["First login", "Verify name prompt"]),
    ("Onboarding", "Verify dismissal", ["Dismiss welcome", "Verify not shown again"]),
    ("Onboarding", "Verify docs link", ["Click docs", "Verify external nav"]),
    ("Onboarding", "Verify support link", ["Click support", "Verify info"]),
    ("Onboarding", "Verify strict mode warning", ["Check initial warning", "Verify acceptance"]),

    # Accessibility (15 tests)
    ("Accessibility", "Verify full keyboard nav", ["Tab through UI", "Verify focus indicators"]),
    ("Accessibility", "Verify screen reader ARIA", ["Inspect elements", "Verify aria-labels"]),
    ("Accessibility", "Verify heading structure", ["Inspect headings", "Verify hierarchy"]),
    ("Accessibility", "Verify high contrast mode", ["Enable high contrast", "Verify colors"]),
    ("Accessibility", "Verify focus management", ["Open modal", "Verify focus trapped"]),
    ("Accessibility", "Verify escape key", ["Press Esc", "Verify modal closes"]),
    ("Accessibility", "Verify skip links", ["Tab first", "Verify skip to content"]),
    ("Accessibility", "Verify form labels", ["Inspect inputs", "Verify labels exist"]),
    ("Accessibility", "Verify error announcements", ["Trigger error", "Verify aria-live"]),
    ("Accessibility", "Verify resizing text", ["Zoom 200%", "Verify layout integrity"]),
    ("Accessibility", "Verify interactive specs", ["Check button sizes", "Verify >44px"]),
    ("Accessibility", "Verify color contrast", ["Audit colors", "Verify AA standard"]),
    ("Accessibility", "Verify alt text", ["Inspect images", "Verify alt attributes"]),
    ("Accessibility", "Verify reduced motion", ["Enable preference", "Verify transitions off"]),
    ("Accessibility", "Verify keyboard shortcuts access", ["Test all shortcuts", "Verify functionality"]),

    # Responsive Design (10 tests)
    ("Responsive", "Verify mobile layout", ["Resize to <768px", "Verify single column"]),
    ("Responsive", "Verify hamburger menu", ["Click menu", "Verify sidebar toggle"]),
    ("Responsive", "Verify tablet layout", ["Resize to 768-1024px", "Verify 2-col layout"]),
    ("Responsive", "Verify desktop layout", ["Resize >1024px", "Verify 3-col layout"]),
    ("Responsive", "Verify touch inputs", ["Simulate touch", "Verify tap targets"]),
    ("Responsive", "Verify artifact mobile view", ["Open artifact mobile", "Verify overlay"]),
    ("Responsive", "Verify swipe gestures", ["Swipe sidebar", "Verify open/close"]),
    ("Responsive", "Verify input adjustment mobile", ["Focus input mobile", "Verify viewport height"]),
    ("Responsive", "Verify PWA manifest", ["Check manifest", "Verify valid"]),
    ("Responsive", "Verify rotation handling", ["Rotate device", "Verify layout adapts"]),

    # API & Backend (15 tests)
    ("Backend", "Verify health check", ["GET /health", "Verify 200 OK"]),
    ("Backend", "Verify auth endpoints", ["POST /login", "Verify token returned"]),
    ("Backend", "Verify conversation CRUD", ["Test GET/POST/PUT/DELETE", "Verify success"]),
    ("Backend", "Verify message streaming", ["Connect SSE", "Verify data packets"]),
    ("Backend", "Verify error handling", ["Send invalid ID", "Verify 404/400"]),
    ("Backend", "Verify rate limiting (mock)", ["Spam requests", "Verify 429"]),
    ("Backend", "Verify invalid payload", ["Send bad JSON", "Verify 400"]),
    ("Backend", "Verify unauthorized access", ["No token", "Verify 401"]),
    ("Backend", "Verify forbidden access", ["Wrong user resource", "Verify 403"]),
    ("Backend", "Verify database migrations", ["Check startup", "Verify tables created"]),
    ("Backend", "Verify CORS headers", ["Check response", "Verify allowed origins"]),
    ("Backend", "Verify static asset serving", ["Request logo", "Verify 200"]),
    ("Backend", "Verify artifact endpoints", ["Test artifact CRUD", "Verify success"]),
    ("Backend", "Verify project endpoints", ["Test project CRUD", "Verify success"]),
    ("Backend", "Verify cleanup tasks", ["Check old temp files", "Verify removal"]),
]

# Convert detailed tests to strict dict format
final_tests = []
for cat, desc, steps in detailed_tests:
    final_tests.append({
        "category": cat,
        "description": desc,
        "steps": steps,
        "passes": False
    })

# If we are short of 200, fill with generic but specific numbered ones
current_count = len(final_tests)
needed = 200 - current_count

if needed > 0:
    for i in range(needed):
         final_tests.append({
        "category": "General Robustness",
        "description": f"Extended robust functionality test case #{i+1}",
        "steps": ["Perform stress test action", "Verify stability", "Check logs"],
        "passes": False
    })

print(json.dumps(final_tests, indent=2))
