import os
import json
import random
import re
from datetime import datetime
from typing import Dict, Any

# Try to import LangChain + Gemini integration. If unavailable, fall back to a
# local deterministic generator so the backend is runnable without external API keys.

USE_GEMINI_API = bool(os.getenv("AIzaSyCiDZKp5Q-0UXMIRJilEc6Z8WlqxlRVU1E"))


def _simple_sentence_split(text: str):
    # crude split on sentences
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 20]


class LLMQuizGenerator:
    def __init__(self):
        # If you want to wire up LangChain + Gemini, do it here.
        # For now we default to the simple fallback.
        self.use_gemini = USE_GEMINI

    def generate_quiz(self, article_title: str, article_text: str, num_questions: int = 5) -> Dict[str, Any]:
        if self.use_gemini:
            # TODO: implement real LangChain + Gemini chain here.
            # Placeholder for future integration.
            try:
                from langchain import LLMChain, PromptTemplate
                from langchain.output_parsers import PydanticOutputParser
                # Actual integration would go here; raising NotImplementedError for now
                raise NotImplementedError("Gemini integration not implemented in this scaffold")
            except Exception as e:
                # Fall back to simple generator on any error
                print("Gemini path failed, falling back to local generator:", e)
                return self._fallback_generate(article_title, article_text, num_questions)

        return self._fallback_generate(article_title, article_text, num_questions)

    def _fallback_generate(self, title: str, text: str, num_questions: int = 5) -> Dict[str, Any]:
        sentences = _simple_sentence_split(text)
        if not sentences:
            sentences = [text[:200]]

        # Pick candidate sentences as sources for questions
        chosen = []
        idx = 0
        while len(chosen) < num_questions and idx < len(sentences):
            chosen.append(sentences[idx])
            idx += max(1, len(sentences) // (num_questions + 1))

        questions = []
        for i, sent in enumerate(chosen):
            q_text = self._make_question_from_sentence(sent)
            correct = self._shorten(sent)

            # Build distractors by sampling other sentence fragments
            distractors = set()
            attempts = 0
            while len(distractors) < 3 and attempts < 20:
                candidate = random.choice(sentences)
                frag = self._shorten(candidate)
                if frag != correct:
                    distractors.add(frag[:120])
                attempts += 1

            options = list(distractors)
            options.append(correct)
            random.shuffle(options)
            correct_index = options.index(correct)

            questions.append({
                "question": q_text,
                "options": options,
                "correct_index": correct_index,
                "explanation": f"Answer derived from sentence: \"{sent[:150]}\""
            })

        quiz = {
            "title": title,
            "summary": (text[:800] + "...") if len(text) > 800 else text,
            "keywords": self._extract_keywords(text),
            "questions": questions,
            "source_url": None,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
        return quiz

    def _shorten(self, s: str, max_len: int = 120) -> str:
        s = re.sub(r"\s+", " ", s).strip()
        return (s[:max_len] + "...") if len(s) > max_len else s

    def _make_question_from_sentence(self, s: str) -> str:
        # Very simple heuristic: convert a sentence into a "What is..." question
        s = s.strip()
        # if contains ' is ' or ' are ' try to ask "What is X?"
        if " is " in s:
            subj = s.split(" is ", 1)[0]
            subj = re.sub(r"^[Tt]he\s", "", subj)
            return f"According to the article, what is {subj.strip()}?"
        # fallback
        short = self._shorten(s, 80)
        return f"Which of the following is true about: {short}"

    def _extract_keywords(self, text: str, max_k: int = 8):
        # naive keyword extraction: top N frequent non-stop words
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        stop = set(["which","this","that","there","their","about","have","would","should","these","those","other","using","using","using"]) 
        freq = {}
        for w in words:
            if w in stop:
                continue
            freq[w] = freq.get(w, 0) + 1
        items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in items[:max_k]]
