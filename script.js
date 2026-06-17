(() => {
  const state = {
    activeMode: "dictionary",
    data: [],
    qaData: [],
    mcqData: [],
    index: [],
    qaIndex: [],
    mcqIndex: [],
    synonymIndex: new Map(),
    wordMap: new Map(),
    results: [],
    page: 0,
    pageSize: 30,
    query: "",
    bookmarks: new Set(),
    recent: []
  };

  const qs = (sel) => document.querySelector(sel);
  const qsa = (sel) => Array.from(document.querySelectorAll(sel));
  const page = document.body.dataset.page;

  document.addEventListener("DOMContentLoaded", async () => {
    initTheme();
    loadUserData();
    await loadData();

    if (page === "home") {
      initHome();
      updateStats();
      renderWordOfDay();
      renderRecent();
      hydrateQueryFromUrl();
    }

    if (page === "word") initWordPage();
    if (page === "bookmarks") initBookmarks();
  });

  async function loadData() {
    try {
      const [wordsRes, qaRes, mcqRes] = await Promise.all([
        fetch("data.json"),
        fetch("Ques-ans-data.json"),
        fetch("Mcqs-data.json")
      ]);
      if (!wordsRes.ok) throw new Error(`data.json HTTP ${wordsRes.status}`);

      const wordsRaw = await wordsRes.json();
      state.data = wordsRaw.map(normalizeEntry).filter(Boolean);

      if (qaRes.ok) {
        const qaRaw = await qaRes.json();
        state.qaData = qaRaw.map(normalizeQaEntry).filter(Boolean);
      }

      if (mcqRes.ok) {
        const mcqRaw = await mcqRes.json();
        state.mcqData = mcqRaw.map(normalizeMcqEntry).filter(Boolean);
      }

      buildIndexes();
    } catch (err) {
      console.error("Failed to load site data", err);
      state.data = [];
      state.qaData = [];
      state.mcqData = [];
    }
  }

  function normalizeEntry(entry) {
    if (!entry || !entry.word) return null;

    const explanationValue = entry.explanation || entry.Explanation || "";
    const synonyms = ensureArray(entry.synonyms);
    const antonyms = ensureArray(entry.antonyms);
    const collocations = ensureArray(entry.collocations);
    const examples = [entry.example, entry.example2, entry.example3]
      .map((ex) => String(ex || "").trim())
      .filter(Boolean);

    return {
      word: String(entry.word || "").trim(),
      meaning: String(entry.meaning || "").trim(),
      shortMeaning: String(entry.shortMeaning || "").trim(),
      example: String(entry.example || "").trim(),
      example2: String(entry.example2 || "").trim(),
      example3: String(entry.example3 || "").trim(),
      explanation: String(explanationValue || "").trim(),
      synonyms,
      antonyms,
      nounForm: String(entry.nounForm || "").trim(),
      verbForm: String(entry.verbForm || "").trim(),
      adjectiveForm: String(entry.adjectiveForm || "").trim(),
      partOfSpeech: String(entry.partOfSpeech || "").trim(),
      commonContext: String(entry.commonContext || "").trim(),
      usageTip: String(entry.usageTip || "").trim(),
      commonMistake: String(entry.commonMistake || "").trim(),
      collocations,
      examples
    };
  }

  function ensureArray(value) {
    if (!Array.isArray(value)) return [];
    return value.map((v) => String(v || "").trim()).filter(Boolean);
  }

  function normalizeQaEntry(entry) {
    if (!entry || !entry.word) return null;

    const questions = [];
    for (let i = 1; i <= 10; i += 1) {
      const question = String(entry[`Question${i}`] || "").trim();
      const answer = String(entry[`Answer${i}`] || "").trim();
      if (question || answer) questions.push({ question, answer });
    }

    if (!questions.length) return null;

    return {
      word: String(entry.word || "").trim(),
      questions
    };
  }

  function normalizeMcqEntry(entry) {
    if (!entry || !entry.word) return null;

    const mcqs = [];
    for (let i = 1; i <= 10; i += 1) {
      const question = String(entry[`mcqs${i}`] || "").trim();
      const options = [1, 2, 3, 4]
        .map((optionNumber) => String(entry[`mcqs${i}Option${optionNumber}`] || "").trim())
        .filter(Boolean);
      const correctAnswer = String(entry[`mcqs${i}CorrectAnswer`] || "").trim();
      const explanation = String(entry[`mcqs${i}Explanation`] || "").trim();

      if (question || options.length || correctAnswer || explanation) {
        mcqs.push({ question, options, correctAnswer, explanation });
      }
    }

    if (!mcqs.length) return null;

    return {
      word: String(entry.word || "").trim(),
      mcqs
    };
  }

  function buildIndexes() {
    state.wordMap = new Map();
    state.synonymIndex = new Map();

    state.index = state.data.map((entry, idx) => {
      const normalizedWord = normalizeSearchTerm(entry.word);

      const searchText = [
        entry.word,
        entry.shortMeaning,
        entry.meaning,
        entry.explanation,
        entry.partOfSpeech,
        entry.commonContext,
        entry.usageTip,
        entry.commonMistake,
        entry.nounForm,
        entry.verbForm,
        entry.adjectiveForm,
        entry.synonyms.join(" "),
        entry.antonyms.join(" "),
        entry.collocations.join(" "),
        entry.examples.join(" ")
      ].join(" ").toLowerCase();

      state.wordMap.set(normalizedWord, entry);

      entry.synonyms.forEach((syn) => {
        const key = normalizeSearchTerm(syn);
        if (!state.synonymIndex.has(key)) state.synonymIndex.set(key, new Set());
        state.synonymIndex.get(key).add(idx);
      });

      return {
        idx,
        word: normalizedWord,
        searchText,
        synonymsText: entry.synonyms.join(" ").toLowerCase(),
        collocationsText: entry.collocations.join(" ").toLowerCase()
      };
    });

    state.qaIndex = state.qaData.map((entry, idx) => ({
      idx,
      word: normalizeSearchTerm(entry.word),
      searchText: [entry.word, ...entry.questions.flatMap((item) => [item.question, item.answer])]
        .join(" ")
        .toLowerCase()
    }));

    state.mcqIndex = state.mcqData.map((entry, idx) => ({
      idx,
      word: normalizeSearchTerm(entry.word),
      searchText: [
        entry.word,
        ...entry.mcqs.flatMap((item) => [
          item.question,
          item.correctAnswer,
          item.explanation,
          ...item.options
        ])
      ]
        .join(" ")
        .toLowerCase()
    }));
  }

  function initTheme() {
    const stored = localStorage.getItem("leximera-theme") || "light";
    setTheme(stored);
    const toggle = qs("#themeToggle");
    if (!toggle) return;

    toggle.addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      setTheme(next);
    });
  }

  function setTheme(mode) {
    document.documentElement.dataset.theme = mode;
    localStorage.setItem("leximera-theme", mode);
    const icon = qs("#themeIcon");
    if (icon) icon.textContent = mode === "dark" ? "◑" : "◐";
  }

  function loadUserData() {
    try {
      const stored = JSON.parse(localStorage.getItem("leximera-bookmarks") || "[]");
      state.bookmarks = new Set(Array.isArray(stored) ? stored : []);
    } catch (err) {
      state.bookmarks = new Set();
    }

    try {
      const storedRecent = JSON.parse(localStorage.getItem("leximera-recent") || "[]");
      state.recent = Array.isArray(storedRecent) ? storedRecent : [];
    } catch (err) {
      state.recent = [];
    }
  }

  function saveBookmarks() {
    localStorage.setItem("leximera-bookmarks", JSON.stringify([...state.bookmarks]));
  }

  function saveRecent() {
    localStorage.setItem("leximera-recent", JSON.stringify(state.recent));
  }

  function initHome() {
    const input = qs("#searchInput");
    const clearBtn = qs("#clearSearch");
    const loadMore = qs("#loadMore");

    if (input) {
      input.addEventListener("input", debounce(handleSearchInput, 300));
      input.addEventListener("keydown", handleSearchKeys);
    }

    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        if (input) input.value = "";
        state.query = "";
        hideSuggestions();
        clearBtn.style.display = "none";
        performSearch("");
      });
    }

    if (loadMore) loadMore.addEventListener("click", () => renderResults(false));

    const refresh = qs("#refreshWord");
    if (refresh) refresh.addEventListener("click", () => renderWordOfDay(true));

    const clearRecent = qs("#clearRecent");
    if (clearRecent) {
      clearRecent.addEventListener("click", () => {
        state.recent = [];
        saveRecent();
        renderRecent();
      });
    }

    initModeSwitcher();

    document.addEventListener("click", (event) => {
      const suggestions = qs("#suggestions");
      const searchBox = qs(".search-box");
      if (!suggestions || !searchBox) return;
      if (!searchBox.contains(event.target) && !suggestions.contains(event.target)) hideSuggestions();
    });
  }

  function hydrateQueryFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const q = (params.get("q") || "").trim();
    if (!q) return;

    const input = qs("#searchInput");
    const clearBtn = qs("#clearSearch");
    if (input) input.value = q;
    if (clearBtn) clearBtn.style.display = "inline-flex";

    state.query = q;
    performSearch(q);
  }

  function updateStats() {
    const totalWords = qs("#totalWords");
    const totalSynonyms = qs("#totalSynonyms");
    const totalExamples = qs("#totalExamples");
    const totalWordsLabel = qs("#totalWordsLabel");
    const totalSynonymsLabel = qs("#totalSynonymsLabel");
    const totalExamplesLabel = qs("#totalExamplesLabel");

    if (state.activeMode === "qa") {
      const questionCount = state.qaData.reduce((acc, entry) => acc + entry.questions.length, 0);
      const answerCount = questionCount;

      if (totalWords) totalWords.textContent = state.qaData.length.toLocaleString();
      if (totalSynonyms) totalSynonyms.textContent = questionCount.toLocaleString();
      if (totalExamples) totalExamples.textContent = answerCount.toLocaleString();
      if (totalWordsLabel) totalWordsLabel.textContent = "Q/A terms";
      if (totalSynonymsLabel) totalSynonymsLabel.textContent = "Questions";
      if (totalExamplesLabel) totalExamplesLabel.textContent = "Answers";
      return;
    }

    if (state.activeMode === "mcq") {
      const mcqCount = state.mcqData.reduce((acc, entry) => acc + entry.mcqs.length, 0);
      const optionCount = state.mcqData.reduce(
        (acc, entry) => acc + entry.mcqs.reduce((sum, mcq) => sum + mcq.options.length, 0),
        0
      );

      if (totalWords) totalWords.textContent = state.mcqData.length.toLocaleString();
      if (totalSynonyms) totalSynonyms.textContent = mcqCount.toLocaleString();
      if (totalExamples) totalExamples.textContent = optionCount.toLocaleString();
      if (totalWordsLabel) totalWordsLabel.textContent = "MCQ terms";
      if (totalSynonymsLabel) totalSynonymsLabel.textContent = "MCQs";
      if (totalExamplesLabel) totalExamplesLabel.textContent = "Options";
      return;
    }

    if (totalWords) totalWords.textContent = state.data.length.toLocaleString();

    const synonymCount = state.data.reduce((acc, entry) => acc + entry.synonyms.length, 0);
    if (totalSynonyms) totalSynonyms.textContent = synonymCount.toLocaleString();

    const exampleCount = state.data.reduce((acc, entry) => acc + entry.examples.length, 0);
    if (totalExamples) totalExamples.textContent = exampleCount.toLocaleString();
    if (totalWordsLabel) totalWordsLabel.textContent = "Total words";
    if (totalSynonymsLabel) totalSynonymsLabel.textContent = "Synonyms";
    if (totalExamplesLabel) totalExamplesLabel.textContent = "Examples";
  }

  function initModeSwitcher() {
    qsa(".mode-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const nextMode = btn.dataset.mode || "dictionary";
        if (nextMode === state.activeMode) return;

        state.activeMode = nextMode;
        qsa(".mode-btn").forEach((el) => el.classList.toggle("active", el === btn));
        hideSuggestions();
        updateStats();
        performSearch(state.query);
      });
    });
  }

  function handleSearchInput(event) {
    state.query = event.target.value.trim();
    const clearBtn = qs("#clearSearch");
    if (clearBtn) clearBtn.style.display = state.query ? "inline-flex" : "none";
    performSearch(state.query);
  }

  function handleSearchKeys(event) {
    const items = qsa(".suggestion");
    if (!items.length) return;

    let activeIndex = items.findIndex((item) => item.classList.contains("active"));

    if (event.key === "ArrowDown") {
      event.preventDefault();
      activeIndex = (activeIndex + 1) % items.length;
      setActiveSuggestion(items, activeIndex);
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      activeIndex = activeIndex <= 0 ? items.length - 1 : activeIndex - 1;
      setActiveSuggestion(items, activeIndex);
    }

    if (event.key === "Enter") {
      event.preventDefault();
      const active = items[activeIndex];
      if (active) openWordOrSearch(active.dataset.word);
    }
  }

  function setActiveSuggestion(items, index) {
    items.forEach((item) => item.classList.remove("active"));
    const selected = items[index];
    if (!selected) return;

    selected.classList.add("active");
    selected.scrollIntoView({ block: "nearest" });
  }

  function performSearch(query) {
    const source = getActiveData();

    if (!source.length) {
      setResultsMeta("Data is still loading.");
      return;
    }

    if (!query) {
      state.results = [];
      resetResults();
      hideSuggestions();
      setResultsMeta(getEmptySearchMessage());
      return;
    }

    const results = search(query);
    state.results = results;
    state.page = 0;
    renderResults(true);
    renderSuggestions(results, query);
  }

  function search(query) {
    if (state.activeMode === "qa") return searchSimple(query, state.qaData, state.qaIndex);
    if (state.activeMode === "mcq") return searchSimple(query, state.mcqData, state.mcqIndex);

    const term = normalizeSearchTerm(query);
    if (!term) return [];

    const matches = [];

    for (const item of state.index) {
      const entry = state.data[item.idx];

      let score = 0;

      if (item.word === term) score += 1200;
      if (item.word.startsWith(term)) score += 900;
      if (item.word.includes(term)) score += 520;

      if (item.synonymsText.includes(term)) score += 420;
      if (item.collocationsText.includes(term)) score += 390;
      if (entry.shortMeaning.toLowerCase().includes(term)) score += 280;
      if (entry.meaning.toLowerCase().includes(term)) score += 230;
      if (entry.commonContext.toLowerCase().includes(term)) score += 170;

      if (!score && item.searchText.includes(term)) score += 120;
      if (!score) score = fuzzyWordScore(item.word, term);

      if (score > 0) matches.push({ entry, score });
    }

    matches.sort((a, b) => b.score - a.score || a.entry.word.localeCompare(b.entry.word));
    return matches.map((m) => m.entry);
  }

  function searchSimple(query, source, index) {
    const term = normalizeSearchTerm(query);
    if (!term) return [];

    const matches = [];

    for (const item of index) {
      const entry = source[item.idx];
      let score = 0;

      if (item.word === term) score += 1000;
      if (item.word.startsWith(term)) score += 800;
      if (item.word.includes(term)) score += 500;
      if (item.searchText.includes(term)) score += 180;
      if (!score) score = fuzzyWordScore(item.word, term);

      if (score > 0) matches.push({ entry, score });
    }

    matches.sort((a, b) => b.score - a.score || a.entry.word.localeCompare(b.entry.word));
    return matches.map((m) => m.entry);
  }

  function getActiveData() {
    if (state.activeMode === "qa") return state.qaData;
    if (state.activeMode === "mcq") return state.mcqData;
    return state.data;
  }

  function getEmptySearchMessage() {
    if (state.activeMode === "qa") return "Search a word to see its questions and answers.";
    if (state.activeMode === "mcq") return "Search a word to see its MCQs.";
    return "Start typing to discover words.";
  }

  function renderSuggestions(results, query) {
    const container = qs("#suggestions");
    if (!container) return;

    if (!query) {
      hideSuggestions();
      return;
    }

    const top = results.slice(0, 8);
    if (!top.length) {
      container.innerHTML = `<div class="suggestion"><span>No results for "${escapeHtml(query)}"</span></div>`;
      container.style.display = "block";
      return;
    }

    container.innerHTML = "";
    top.forEach((entry) => {
      const div = document.createElement("div");
      div.className = "suggestion";
      div.dataset.word = entry.word;
      div.innerHTML = `
        <div class="term">${highlight(entry.word, query)}</div>
        <div class="meta">${highlight(getEntryPreview(entry), query)}</div>
      `;
      div.addEventListener("click", () => {
        const input = qs("#searchInput");
        if (input) input.value = entry.word;
        state.query = entry.word;
        hideSuggestions();
        performSearch(state.query);
      });
      container.appendChild(div);
    });

    container.style.display = "block";
  }

  function hideSuggestions() {
    const container = qs("#suggestions");
    if (container) container.style.display = "none";
  }

  function resetResults() {
    const list = qs("#resultsList");
    const loadMore = qs("#loadMore");
    if (list) list.innerHTML = "";
    if (loadMore) loadMore.style.display = "none";
  }

  function renderResults(reset) {
    const list = qs("#resultsList");
    const loadMore = qs("#loadMore");
    if (!list) return;

    if (reset) list.innerHTML = "";

    const start = state.page * state.pageSize;
    const end = start + state.pageSize;
    const slice = state.results.slice(start, end);

    const fragment = document.createDocumentFragment();

    slice.forEach((entry) => {
      const card = document.createElement("article");
      card.className = state.activeMode === "mcq" ? "result-card mcq-card" : "result-card";
      card.innerHTML = renderResultCard(entry);
      if (state.activeMode === "dictionary") card.addEventListener("click", () => navigateToWord(entry.word));
      fragment.appendChild(card);
    });

    list.appendChild(fragment);
    state.page += 1;

    if (loadMore) loadMore.style.display = end < state.results.length ? "block" : "none";

    if (state.results.length) setResultsMeta(`${state.results.length.toLocaleString()} results`);
    else if (state.query || state.activeMode !== "dictionary") setResultsMeta("No results found.");
  }

  function renderResultCard(entry) {
    if (state.activeMode === "qa") {
      return `
        <h4>${highlight(entry.word, state.query)}</h4>
        <div class="meta-row">
          <span class="badge">${entry.questions.length} questions</span>
        </div>
        <div class="qa-list">
          ${entry.questions.map((item, index) => `
            <div class="qa-item">
              <strong>Q${index + 1}. ${highlight(item.question, state.query)}</strong>
              <p>${highlight(item.answer, state.query)}</p>
            </div>
          `).join("")}
        </div>
      `;
    }

    if (state.activeMode === "mcq") {
      return `
        <h4>${highlight(entry.word, state.query)}</h4>
        <div class="meta-row">
          <span class="badge">${entry.mcqs.length} MCQs</span>
        </div>
        <div class="qa-list">
          ${entry.mcqs.map((item, index) => `
            <div class="qa-item">
              <strong class="mcq-question">Q${index + 1}. ${highlight(item.question, state.query)}</strong>
              <div class="mcq-options">
                ${item.options.map((option, optionIndex) => `
                  <div class="mcq-option">${String.fromCharCode(65 + optionIndex)}. ${highlight(option, state.query)}</div>
                `).join("")}
              </div>
              <div class="mcq-answer"><span class="badge">Answer: ${highlight(item.correctAnswer, state.query)}</span></div>
              <p class="mcq-explanation">${highlight(item.explanation, state.query)}</p>
            </div>
          `).join("")}
        </div>
      `;
    }

    return `
      <h4>${highlight(entry.word, state.query)}</h4>
      <p>${highlight(entry.shortMeaning || entry.meaning, state.query)}</p>
      <div class="meta-row">
        <span class="badge">${escapeHtml(entry.partOfSpeech || "word")}</span>
        <span class="badge">${entry.synonyms.length} synonyms</span>
      </div>
    `;
  }

  function getEntryPreview(entry) {
    if (state.activeMode === "qa") {
      const first = entry.questions[0];
      return first ? first.question : "";
    }

    if (state.activeMode === "mcq") {
      const first = entry.mcqs[0];
      return first ? first.question : "";
    }

    return entry.shortMeaning || entry.meaning;
  }

  function setResultsMeta(text) {
    const meta = qs("#resultsMeta");
    if (meta) meta.textContent = text;
  }

  function renderWordOfDay(randomize = false) {
    const container = qs("#wordOfDay");
    if (!container || !state.data.length) return;

    const entry = randomize
      ? state.data[Math.floor(Math.random() * state.data.length)]
      : state.data[daySeed() % state.data.length];

    container.innerHTML = `
      <div class="mini-item" data-word="${escapeHtml(entry.word)}">
        <strong>${escapeHtml(entry.word)}</strong>
        <p>${escapeHtml(entry.shortMeaning || entry.meaning)}</p>
      </div>
    `;

    const item = container.querySelector(".mini-item");
    if (item) item.addEventListener("click", () => navigateToWord(entry.word));
  }

  function daySeed() {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 0);
    const day = Math.floor((now - start) / 86400000);
    return now.getFullYear() * 1000 + day;
  }

  function renderRecent() {
    const list = qs("#recentList");
    if (!list) return;

    if (!state.recent.length) {
      list.innerHTML = `<div class="mini-item">No recent words yet.</div>`;
      return;
    }

    list.innerHTML = "";
    state.recent.slice(0, 8).forEach((item) => {
      const entry = findByWord(item.word);
      if (!entry) return;

      const div = document.createElement("div");
      div.className = "mini-item";
      div.innerHTML = `<strong>${escapeHtml(entry.word)}</strong><p>${escapeHtml(entry.shortMeaning || entry.meaning)}</p>`;
      div.addEventListener("click", () => navigateToWord(entry.word));
      list.appendChild(div);
    });
  }

  function initWordPage() {
    const params = new URLSearchParams(window.location.search);
    const term = (params.get("term") || "").trim();
    const entry = term ? findByWord(term) : null;

    if (!entry) {
      renderNotFound(term);
      return;
    }

    addRecent(entry.word);
    renderWordDetail(entry);
    renderRelated(entry);
  }

  function renderWordDetail(entry) {
    const container = qs("#wordDetail");
    if (!container) return;

    const isBookmarked = state.bookmarks.has(entry.word);
    const examples = entry.examples.length ? entry.examples : ["No examples available."];

    container.innerHTML = `
      <div class="word-title">
        <div>
          <h1>${escapeHtml(entry.word)}</h1>
          <p class="lead">${escapeHtml(entry.shortMeaning || "No short meaning available.")}</p>
          <div class="meta-row">
            <span class="badge">${escapeHtml(entry.partOfSpeech || "Part of speech unavailable")}</span>
          </div>
        </div>
        <div class="word-actions">
          <button class="action-btn" id="bookmarkBtn">${isBookmarked ? "Bookmarked" : "Bookmark"}</button>
          <button class="action-btn" id="speakBtn">Speak</button>
        </div>
      </div>

      <div class="detail-block">
        <h3>Full meaning</h3>
        <p>${escapeHtml(entry.meaning || "No meaning available.")}</p>
      </div>

      <div class="detail-block">
        <h3>Word forms</h3>
        <div class="tag-list">
          <span class="tag">Noun: ${escapeHtml(entry.nounForm || "N/A")}</span>
          <span class="tag">Verb: ${escapeHtml(entry.verbForm || "N/A")}</span>
          <span class="tag">Adjective: ${escapeHtml(entry.adjectiveForm || "N/A")}</span>
        </div>
      </div>

      <div class="detail-block">
        <h3>Examples</h3>
        ${examples.map((ex) => `<div class="example">${escapeHtml(ex)}</div>`).join("")}
      </div>

      <div class="detail-block">
        <details open>
          <summary><strong>Detailed explanation</strong></summary>
          <p>${escapeHtml(entry.explanation || "No explanation available.")}</p>
        </details>
      </div>

      <div class="detail-block">
        <h3>Synonyms</h3>
        <div class="tag-list">${renderTags(entry.synonyms, "synonym", "lookup")}</div>
      </div>

      <div class="detail-block">
        <h3>Antonyms</h3>
        <div class="tag-list">${renderTags(entry.antonyms, "antonym", "lookup")}</div>
      </div>

      <div class="detail-block">
        <h3>Collocations</h3>
        <div class="tag-list">${renderTags(entry.collocations, "collocation", "search")}</div>
      </div>

      <div class="detail-block info-box">
        <h3>Common context</h3>
        <p>${escapeHtml(entry.commonContext || "No context available.")}</p>
      </div>

      <div class="detail-block info-box">
        <h3>Usage tip</h3>
        <p>${escapeHtml(entry.usageTip || "No usage tip available.")}</p>
      </div>

      <div class="detail-block warn-box">
        <h3>Common mistake</h3>
        <p>${escapeHtml(entry.commonMistake || "No common mistake listed.")}</p>
      </div>
    `;

    const bookmarkBtn = qs("#bookmarkBtn");
    if (bookmarkBtn) {
      bookmarkBtn.addEventListener("click", () => {
        toggleBookmark(entry.word);
        bookmarkBtn.textContent = state.bookmarks.has(entry.word) ? "Bookmarked" : "Bookmark";
      });
    }

    const speakBtn = qs("#speakBtn");
    if (speakBtn) speakBtn.addEventListener("click", () => speak(entry.word));

    qsa("button.tag[data-word]").forEach((tag) => {
      tag.addEventListener("click", () => openWordOrSearch(tag.dataset.word));
    });

    qsa("button.tag[data-search]").forEach((tag) => {
      tag.addEventListener("click", () => navigateToSearch(tag.dataset.search));
    });
  }

  function renderTags(list, type, behavior) {
    if (!list.length) return `<span class="tag">No ${type}s</span>`;

    if (behavior === "search") {
      return list
        .map((item) => `<button class="tag" type="button" data-search="${escapeHtml(item)}">${escapeHtml(item)}</button>`)
        .join("");
    }

    return list
      .map((item) => `<button class="tag" type="button" data-word="${escapeHtml(item)}">${escapeHtml(item)}</button>`)
      .join("");
  }

  function renderRelated(entry) {
    const container = qs("#relatedWords");
    const meta = qs("#relatedMeta");
    if (!container) return;

    const related = getRelated(entry, 6).filter(Boolean);
    if (!related.length) {
      container.innerHTML = `<div class="result-card">No related words found.</div>`;
      if (meta) meta.textContent = "";
      return;
    }

    const fragment = document.createDocumentFragment();
    related.forEach((item) => {
      const card = document.createElement("article");
      card.className = "result-card";
      card.innerHTML = `
        <h4>${escapeHtml(item.word)}</h4>
        <p>${escapeHtml(item.shortMeaning || item.meaning)}</p>
      `;
      card.addEventListener("click", () => navigateToWord(item.word));
      fragment.appendChild(card);
    });

    container.innerHTML = "";
    container.appendChild(fragment);

    if (meta) meta.textContent = `${related.length} related words`;
  }

  function getRelated(entry, limit) {
    const scores = new Map();

    entry.synonyms.forEach((syn) => {
      const matches = state.synonymIndex.get(normalizeSearchTerm(syn));
      if (!matches) return;

      matches.forEach((idx) => {
        const word = state.data[idx];
        if (!word || word.word === entry.word) return;
        scores.set(word.word, (scores.get(word.word) || 0) + 1);
      });
    });

    return Array.from(scores.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([word]) => findByWord(word));
  }

  function renderNotFound(term) {
    const container = qs("#wordDetail");
    if (!container) return;

    container.innerHTML = `
      <div class="word-detail">
        <h2>Word not found</h2>
        <p>We could not find an entry for "${escapeHtml(term || "")}".</p>
        <p><a href="index.html?q=${encodeURIComponent(term || "")}">Search this term on home page</a></p>
      </div>
    `;
  }

  function initBookmarks() {
    renderBookmarks();

    const clear = qs("#clearBookmarks");
    if (!clear) return;

    clear.addEventListener("click", () => {
      state.bookmarks.clear();
      saveBookmarks();
      renderBookmarks();
    });
  }

  function renderBookmarks() {
    const container = qs("#bookmarksList");
    if (!container) return;

    if (!state.bookmarks.size) {
      container.innerHTML = `<div class="result-card">No bookmarks yet.</div>`;
      return;
    }

    container.innerHTML = "";
    const fragment = document.createDocumentFragment();

    [...state.bookmarks]
      .sort((a, b) => a.localeCompare(b))
      .forEach((word) => {
        const entry = findByWord(word);
        if (!entry) return;

        const card = document.createElement("article");
        card.className = "result-card";
        card.innerHTML = `
          <h4>${escapeHtml(entry.word)}</h4>
          <p>${escapeHtml(entry.shortMeaning || entry.meaning)}</p>
          <div style="margin-top:10px; display:flex; gap:8px;">
            <button class="action-btn" type="button" data-word="${escapeHtml(entry.word)}">Open</button>
            <button class="action-btn" type="button" data-remove="${escapeHtml(entry.word)}">Remove</button>
          </div>
        `;

        const openBtn = card.querySelector("button[data-word]");
        const removeBtn = card.querySelector("button[data-remove]");

        if (openBtn) openBtn.addEventListener("click", () => navigateToWord(entry.word));
        if (removeBtn) {
          removeBtn.addEventListener("click", () => {
            toggleBookmark(entry.word);
            renderBookmarks();
          });
        }

        fragment.appendChild(card);
      });

    container.appendChild(fragment);
  }

  function toggleBookmark(word) {
    if (state.bookmarks.has(word)) state.bookmarks.delete(word);
    else state.bookmarks.add(word);
    saveBookmarks();
  }

  function addRecent(word) {
    state.recent = state.recent.filter((item) => item.word !== word);
    state.recent.unshift({ word, ts: Date.now() });
    state.recent = state.recent.slice(0, 20);
    saveRecent();
  }

  function findByWord(term) {
    if (!term) return null;

    const normalized = normalizeSearchTerm(term);
    const exact = state.wordMap.get(normalized);
    if (exact) return exact;

    let best = null;
    let bestScore = 0;

    for (const entry of state.data) {
      const word = normalizeSearchTerm(entry.word);
      let score = 0;

      if (word.startsWith(normalized)) score = 360;
      else if (normalized.length >= 3 && word.includes(normalized)) score = 240;

      const fuzzy = fuzzyWordScore(word, normalized);
      if (fuzzy > score) score = fuzzy;

      if (score > bestScore) {
        bestScore = score;
        best = entry;
      }
    }

    return bestScore >= 220 ? best : null;
  }

  function openWordOrSearch(term) {
    const match = findByWord(term);
    if (match && normalizeSearchTerm(match.word) === normalizeSearchTerm(term)) {
      navigateToWord(match.word);
      return;
    }
    navigateToSearch(term);
  }

  function navigateToSearch(term) {
    window.location.href = `index.html?q=${encodeURIComponent(term || "")}`;
  }

  function navigateToWord(word) {
    window.location.href = `word.html?term=${encodeURIComponent(word)}`;
  }

  function speak(text) {
    if (!("speechSynthesis" in window)) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.85;
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
  }

  function highlight(text, query) {
    const source = String(text || "");
    if (!query) return escapeHtml(source);
    const safe = escapeHtml(source);
    const regex = new RegExp(`(${escapeRegExp(query)})`, "gi");
    return safe.replace(regex, '<span class="highlight">$1</span>');
  }

  function escapeHtml(text) {
    return String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function escapeRegExp(text) {
    return String(text || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function normalizeSearchTerm(text) {
    return String(text || "").trim().toLowerCase();
  }

  function fuzzyWordScore(word, term) {
    if (!word || !term || term.length < 4) return 0;
    if (Math.abs(word.length - term.length) > 2) return 0;
    if (word[0] !== term[0]) return 0;

    const distance = editDistanceWithinLimit(word, term, 2);
    if (distance === null || distance === 0) return 0;
    if (distance === 1) return 320;
    if (distance === 2) return 230;
    return 0;
  }

  function editDistanceWithinLimit(a, b, limit) {
    if (a === b) return 0;

    const aLen = a.length;
    const bLen = b.length;
    if (Math.abs(aLen - bLen) > limit) return null;

    let prev = new Array(bLen + 1);
    let curr = new Array(bLen + 1);

    for (let j = 0; j <= bLen; j += 1) prev[j] = j;

    for (let i = 1; i <= aLen; i += 1) {
      curr[0] = i;
      let rowMin = curr[0];

      for (let j = 1; j <= bLen; j += 1) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        curr[j] = Math.min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost);
        if (curr[j] < rowMin) rowMin = curr[j];
      }

      if (rowMin > limit) return null;
      [prev, curr] = [curr, prev];
    }

    return prev[bLen] <= limit ? prev[bLen] : null;
  }

  function debounce(fn, wait) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), wait);
    };
  }
})();
