import uuid
import logging
from typing import List, Tuple
from io import BytesIO

import requests  
from pypdf import PdfReader
from huggingface_hub import InferenceClient

from .config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Global Hugging Face text client – token only, model passed per call
hf_text_client = InferenceClient(
    token=settings.hf_api_key,
)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file given its bytes."""
    reader = PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"

    logger.info("Extracted resume text length: %d characters", len(text))
    # Optional: log a small preview
    logger.info("Resume preview: %s", text[:300].replace("\n", " ") if text else "EMPTY")

    return text


class HuggingFaceClient:
    """Adapter for Hugging Face Inference API."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_question(self, role: str, interview_type: str, difficulty: str) -> str:
        prompt = (
            f"You are an interviewer for a {role} role. "
            f"Generate ONE {interview_type} interview question at {difficulty} difficulty. "
            "Return only the question text."
        )
        return self._call_model(prompt)

    def generate_feedback(self, question: str, answer: str) -> Tuple[float, List[str], List[str], str]:
        prompt = (
            "You are an expert interview coach. "
            "Given the interview question and candidate answer, "
            "evaluate on a scale of 0-10 and provide:\n"
            "1) score (just a number)\n"
            "2) 3 strengths as bullet points\n"
            "3) 3 improvements as bullet points\n"
            "4) an improved sample answer.\n\n"
            f"Question: {question}\n"
            f"Answer: {answer}\n"
        )
        raw = self._call_model(prompt)

        score = 7.0
        strengths = ["Good structure", "Relevant examples", "Clear communication"]
        improvements = ["Add more measurable outcomes", "Use STAR format", "Be more concise"]
        suggested = raw[:800]

        return score, strengths, improvements, suggested
    
    def generate_cover_letter(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        resume_text: str,
        tone: str,
    ) -> str:
        prompt = f"""
You are an expert cover letter writer for software engineering internships and new grad roles.

Your task is to write a personalized, truthful cover letter based ONLY on:
1) The candidate's resume
2) The target job description
3) The provided job title and company name

============================
⚠️ STRICT RULES — FOLLOW EXACTLY
============================
1. DO NOT invent or assume experiences, projects, companies, or technologies that are not present in the resume.
2. Use the given job title and company name explicitly in the letter.
3. The cover letter must be written in first person singular ("I").
4. Length: 3–5 short paragraphs.
5. Focus on how the candidate's actual experience and skills match the job description.
6. Emphasize backend, APIs, full-stack, cloud, data, and performance-related experience if relevant.
7. Tone: {tone} (professional, confident, concise).

============================
📄 INPUTS
============================
JOB TITLE: {job_title}
COMPANY NAME: {company_name}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

============================
📤 OUTPUT FORMAT
============================
Return ONLY the cover letter text as plain text.
No markdown headings, no bullet points, no extra labels.
"""
        return self._call_model(prompt)

    def improve_resume(self, resume_text: str, job_description: str) -> str:
        prompt = f"""
You are an expert technical resume reviewer.

Your job is to evaluate the candidate's resume in the context of the job description
and provide ONLY 3–4 short, actionable suggestions to improve the resume.

============================
⚠️ STRICT RULES — FOLLOW EXACTLY
============================
1. DO NOT rewrite the resume.
2. DO NOT output the full resume.
3. DO NOT create fictional experiences or technologies.
4. ONLY return improvement suggestions.
5. Suggestions MUST be based 100% on the resume text provided.
6. Each suggestion must be one sentence.
7. Focus on ATS optimization, quantification, clarity, and technical alignment.

============================
📄 INPUTS
============================
JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

============================
📤 OUTPUT FORMAT (VERY IMPORTANT)
============================

Return ONLY this structure:

SUGGESTIONS:
- <suggestion 1>
- <suggestion 2>
- <suggestion 3>
- <suggestion 4>

If fewer suggestions apply, return 2–3. No extra text.
"""
        return self._call_model(prompt)

    def _call_model(self, prompt: str) -> str:
        if not self.api_key:
            logger.error("Hugging Face API key is not configured.")
            return "Hugging Face API key not configured."

        try:
            text = hf_text_client.text_generation(
                prompt,
                model=settings.hf_model_id,
                max_new_tokens=700,
            )
            logger.info("HF text_generation returned %d characters", len(text))
            return text

        except ValueError as e:
            msg = str(e)
            logger.warning("text_generation not supported for this model: %s", msg)
            if "conversational" not in msg.lower():
                raise

            try:
                # Conversational-style call (chat completion)
                resp = hf_text_client.chat_completion(
                    model=settings.hf_model_id,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=700,
                )
                if isinstance(resp, dict):
                    choices = resp.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content")
                        if content:
                            logger.info(
                                "HF chat_completion returned %d characters",
                                len(content),
                            )
                            return content

                logger.warning("Unexpected chat_completion response format: %s", resp)
                return str(resp)

            except Exception as ee:
                logger.exception(
                    "HF chat_completion also failed for conversational model"
                )
                return "Sorry, I could not generate a response at this time."

        except Exception:
            logger.exception("Unexpected Hugging Face API error via InferenceClient")
            return "Sorry, I could not generate a response at this time."
        

    def rewrite_summary(self, resume_text: str, job_description: str) -> str:
        prompt = f"""
You are an expert technical resume writer.

Your task is to rewrite ONLY the SUMMARY section of the resume so it best matches the job description.

============================
⚠️ STRICT RULES — FOLLOW EXACTLY
============================
1. DO NOT invent new experiences, skills, companies, or technologies.
2. Use ONLY information that already exists in the resume.
3. The new summary must be 2–3 lines maximum.
4. Focus on backend, APIs, full-stack, cloud, data, and performance-related work if relevant to the JD.
5. Optimize wording for ATS and clarity while staying 100% truthful.

============================
📄 INPUTS
============================
JOB DESCRIPTION:
{job_description}

FULL RESUME:
{resume_text}

============================
📤 OUTPUT FORMAT (VERY IMPORTANT)
============================

Return ONLY this:

SUMMARY:
<rewritten 2–3 line summary here>

No additional commentary, no markdown, no bullets.
"""
        return self._call_model(prompt)


hf_client = HuggingFaceClient(settings.hf_api_key)

class CareerService:
    """Facade for cover letter and smart resume features."""

    def generate_cover_letter(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        candidate_summary: str,
        tone: str,
    ) -> str:
        return hf_client.generate_cover_letter(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            candidate_summary=candidate_summary,
            tone=tone,
        )
        
    def generate_cover_letter_from_file(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        tone: str,
        resume_bytes: bytes,
        resume_content_type: str,
    ) -> str:
        """Extract resume text and generate a tailored cover letter."""
        if resume_content_type == "application/pdf":
            resume_text = extract_text_from_pdf(resume_bytes)
        else:
            resume_text = resume_bytes.decode("utf-8", errors="ignore")

        logger.info(
            "Cover letter – resume text length: %d characters",
            len(resume_text),
        )

        return hf_client.generate_cover_letter(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            resume_text=resume_text,
            tone=tone,
        )        

    def improve_resume(self, resume_text: str, job_description: str) -> str:
        return hf_client.improve_resume(
            resume_text=resume_text,
            job_description=job_description,
        )

    def improve_resume_from_file(
        self,
        file_bytes: bytes,
        content_type: str,
        job_description: str,
    ) -> Tuple[str, List[str]]:
        if content_type == "application/pdf":
            resume_text = extract_text_from_pdf(file_bytes)
        else:
            resume_text = file_bytes.decode("utf-8", errors="ignore")

        logger.info("Resume text passed to LLM length: %d", len(resume_text))

        raw_output = hf_client.improve_resume(
            resume_text=resume_text,
            job_description=job_description,
        )

        suggestions = []

        if "SUGGESTIONS:" in raw_output:
            lines = raw_output.split("SUGGESTIONS:", 1)[1].strip().splitlines()
            for line in lines:
                line = line.strip()
                if line.startswith("-"):
                    suggestions.append(line[1:].strip())

        logger.info("Parsed %d suggestions from LLM output", len(suggestions))

        return suggestions

    def rewrite_summary_from_file(
        self,
        file_bytes: bytes,
        content_type: str,
        job_description: str,
    ) -> str:
        """Extract text from uploaded resume and get a rewritten summary from the LLM."""
        if content_type == "application/pdf":
            resume_text = extract_text_from_pdf(file_bytes)
        else:
            resume_text = file_bytes.decode("utf-8", errors="ignore")

        logger.info("Resume text passed to summary rewriter length: %d", len(resume_text))

        raw_output = hf_client.rewrite_summary(
            resume_text=resume_text,
            job_description=job_description,
        )

        summary = raw_output.strip()

        if summary.upper().startswith("SUMMARY:"):
            summary = summary[len("SUMMARY:") :].strip()

        return summary


career_service = CareerService()