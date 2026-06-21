// Hebrew Word of the Day — app logic.
// Deterministic "word of the day" from the date, plus browse + speak.
(function () {
  "use strict";

  const el = (id) => document.getElementById(id);
  const els = {
    date: el("date"),
    pos: el("pos"),
    hebrew: el("hebrew"),
    translit: el("translit"),
    pron: el("pron"),
    gloss: el("gloss"),
    meaning: el("meaning"),
    strongs: el("strongs"),
    occ: el("occ"),
    verseHe: el("verseHe"),
    verseEn: el("verseEn"),
    verseRef: el("verseRef"),
    counter: el("counter"),
    card: el("card"),
    speakBtn: el("speakBtn"),
  };

  const total = WORDS.length;

  // Days since the Unix epoch in the user's local time zone.
  function dayNumber(date) {
    const local = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    return Math.floor(local.getTime() / 86400000);
  }

  // The "anchor" day maps to index 0; index advances one per calendar day and
  // wraps around the list, so everyone on the same date sees the same word.
  const todayIndex = ((dayNumber(new Date()) % total) + total) % total;

  let current = todayIndex;

  const fmtDate = new Intl.DateTimeFormat(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  function render(index, opts) {
    opts = opts || {};
    const w = WORDS[((index % total) + total) % total];
    current = ((index % total) + total) % total;

    if (opts.isToday) {
      els.date.textContent = fmtDate.format(new Date());
    } else {
      const offset = current - todayIndex;
      els.date.textContent = offset === 0 ? fmtDate.format(new Date()) : "Word " + (current + 1);
    }

    els.pos.textContent = w.pos || "";
    els.hebrew.textContent = w.hebrew;
    els.translit.textContent = w.translit;
    els.pron.textContent = w.pron ? "say it: " + w.pron : "";
    els.gloss.textContent = w.gloss;
    els.meaning.textContent = w.meaning;
    els.strongs.textContent = w.strongs ? "Strong's " + w.strongs : "";
    els.occ.textContent =
      w.occurrences != null ? "~" + w.occurrences.toLocaleString() + "× in the Bible" : "";

    els.verseHe.textContent = w.verse ? w.verse.he : "";
    els.verseEn.textContent = w.verse ? "“" + w.verse.en + "”" : "";
    els.verseRef.textContent = w.verse ? "— " + w.verse.ref : "";

    els.counter.textContent = current + 1 + " / " + total;

    // restart the rise animation
    els.card.style.animation = "none";
    void els.card.offsetWidth;
    els.card.style.animation = "";

    cancelSpeech();
  }

  // ---- pronunciation via Web Speech API (best effort) ----
  let heVoice = null;
  function pickHebrewVoice() {
    if (!("speechSynthesis" in window)) return;
    const voices = speechSynthesis.getVoices();
    heVoice =
      voices.find((v) => /^he\b|he[-_]IL|iw/i.test(v.lang)) ||
      voices.find((v) => /hebrew/i.test(v.name)) ||
      null;
  }
  if ("speechSynthesis" in window) {
    pickHebrewVoice();
    speechSynthesis.onvoiceschanged = pickHebrewVoice;
  }

  function cancelSpeech() {
    if ("speechSynthesis" in window) speechSynthesis.cancel();
    els.speakBtn.classList.remove("speaking");
  }

  function speak() {
    if (!("speechSynthesis" in window)) {
      flashUnsupported();
      return;
    }
    const w = WORDS[current];
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(w.hebrew);
    if (heVoice) {
      u.voice = heVoice;
      u.lang = heVoice.lang;
    } else {
      u.lang = "he-IL";
    }
    u.rate = 0.85;
    u.onstart = () => els.speakBtn.classList.add("speaking");
    u.onend = u.onerror = () => els.speakBtn.classList.remove("speaking");
    speechSynthesis.speak(u);
  }

  function flashUnsupported() {
    const prev = els.pron.textContent;
    els.pron.textContent = "Speech not supported on this device — see the guide above.";
    setTimeout(() => (els.pron.textContent = prev), 2200);
  }

  // ---- events ----
  els.speakBtn.addEventListener("click", speak);
  el("prevBtn").addEventListener("click", () => render(current - 1));
  el("nextBtn").addEventListener("click", () => render(current + 1));
  el("todayBtn").addEventListener("click", () => render(todayIndex, { isToday: true }));
  el("randomBtn").addEventListener("click", () => {
    let r = current;
    if (total > 1) while (r === current) r = Math.floor(Math.random() * total);
    render(r);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") render(current - 1);
    else if (e.key === "ArrowRight") render(current + 1);
    else if (e.key === " " || e.key === "Enter") {
      if (e.target === document.body) {
        e.preventDefault();
        speak();
      }
    }
  });

  // ---- swipe navigation ----
  let touchX = null;
  els.card.addEventListener(
    "touchstart",
    (e) => (touchX = e.changedTouches[0].clientX),
    { passive: true }
  );
  els.card.addEventListener(
    "touchend",
    (e) => {
      if (touchX == null) return;
      const dx = e.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 60) render(current + (dx < 0 ? 1 : -1));
      touchX = null;
    },
    { passive: true }
  );

  // ---- install prompt ----
  let deferredPrompt = null;
  const installBtn = el("installBtn");
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installBtn.hidden = false;
  });
  installBtn.addEventListener("click", async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    installBtn.hidden = true;
  });
  window.addEventListener("appinstalled", () => (installBtn.hidden = true));

  // ---- service worker ----
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("service-worker.js").catch(() => {});
    });
  }

  render(todayIndex, { isToday: true });
})();
