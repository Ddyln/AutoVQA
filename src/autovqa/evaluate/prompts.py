from string import Template

EVALUATE_IMAGE_PROMPT = """
You are a professional photo quality judge. Your task is to give a score for each criterion related to a photo that will be submitted and give me the reason why you gave such an assessment (excep object density and scence clutter). The criteria are as follows:

1. img_clarity (Image clarity): Evaluate the clarity of the provided image based on resolution, noise, blurriness, lighting conditions, and detail visibility. Assign a clarity score from 0 to 10 according to this scale:
* 9–10: Very sharp, clear, excellent detail.
* 6–8: Slight blur/noise but identifiable objects.
* 3–5: Significant blur, unclear details.
* 0–2: Severely blurry or corrupted.

2. img_occlusion (Image Occlusion): Evaluate how much the main subject in this image is occluded, cut off, or obscured.Assign an occlusion score from 0 to 10 using this scale:
* 9–10: Fully visible, no occlusion.
* 6–8: Partially occluded (10–30%), still clear.
* 3–5: Heavily occluded, missing major details.
* 0–2: Main subject barely visible or invisible.

3. img_diff_ability (Ability to distinguish between objects): Evaluate how easily distinct objects (especially similar ones) can be differentiated in this image. Consider color, shape, position, or behavior differences. Assign a differentiation score from 0 to 10 according to
* 9–10: Clearly distinguishable, no confusion.
* 6–8: Minor ambiguity, generally distinguishable.
* 3–5: Significant ambiguity, difficult to distinguish clearly.
* 0–2: Objects indistinguishable.

4. img_object_density (number of distinct objects): Determine approximately how many objects are present in the image. Assign a score from 0 to 10 based on:
* 9–10: Over 15 objects clearly identifiable.
* 6–8: 10–15 objects.
* 3–5: 5–9 objects.
* 0–2: Fewer than 5 objects or nearly empty.

5. img_interaction_level (how objects interact): Are the objects and people in the photo interacting with each other (e.g. one person handing an object to another, two teams playing a sport). Assign a score from 0 to 10 based on:
* 9–10: Multiple (>=3) clear interactions.
* 6–8: Two clear interactions.
* 3–5: Mild interactions or ambiguous interactions.
* 0–2: No clear interactions.

6. img_scene_clutter (visual complexity): The level of “clutter” in the scene. A cluttered scene requires strong attention to focus on elements relevant to the question. Assign a score from 0 to 10 based on:
* 9–10: Extremely cluttered, objects overlap significantly.
* 6–8: Moderately cluttered.
* 3–5: Slightly cluttered, manageable.
* 0–2: Very clean, minimalistic.
"""

IMAGE_DIVERSITY_PROMPT = """
You are an expert assessor of visual diversity in image datasets, particularly for evaluating potential cultural and contextual biases.

Your tasks are:

1. **Scene Type** (`Img_scene_type`): Identify the general scene category (e.g., indoor, outdoor, rural, urban, nature, fictional, culturally-specific location, etc.).

2. **Main Object** (`Img_main_object`): Identify the most salient object category in the image (e.g., person, dog, car, boat, etc.). If there are multiple, choose the most prominent one. Preferably use COCO categories if applicable.

3. **Main Object Description** (`Image_mainobj_descrip`): Describe the main object with visual attributes such as:
   - **Color**
   - **Size**
   - **Shape**
   - **Material**
   - **Texture**
   - **State or Action** (e.g., sitting, dancing, broken, glowing...)

4. **Cultural / Geographic Representation** (`Cultural_context`):  
   Identify any **cultural, geographic, or regional elements** present in the image. These could include:
   - Traditional clothing or food  
   - Local landmarks or architecture  
   - Regional activities or tools  
   - Language, signs, or scripts in the image  
   If none are detectable, write `"none"`.

5. **Demographic Cues** (`Demographic_signals`):  
   Does the image suggest any demographic diversity in terms of **age, gender, ethnicity, or ability**? If so, describe briefly. If not present or not inferable, write `"none"`.

6. **Scene Rarity / Typicality** (`Scene_typicality_score`):  
   Rate the scene on a scale from 1 to 5 based on how **typical** or **frequently seen** this scene is in mainstream datasets (e.g., COCO, Visual Genome).  
   - 1 = Very typical (e.g., office, kitchen, living room)  
   - 5 = Very rare or culturally unique (e.g., Mongolian yurt interior, African tribal dance, Vietnamese floating market)
"""

EVALUATE_TEXT_PROMPT = """
You are a modern text evaluation system with the ability to check and comment on Vietnamese text. Your task is to give a score for each criterion related to each elements of QA (1 Question and a list of answer) that will be submitted and give me the reason why you gave such an assessment. The criteria are as follows:
1. txt_grammar (grammar): Check the grammar of the text, including sentence structure, punctuation, and word usage. Provide a score from 0 to 10 based on the following scale:
* 9–10: Fully correct, proper grammar and spelling.
* 6–8: Minor spelling errors, negligible impact. 
* 3–5: Major grammatical issues, significant spelling mistakes.  
* 0–2: Text is incomprehensible or severely flawed.  

2. txt_unambiguity (ambiguity): Evaluate the clarity and precision of the text. Determine if the text is ambiguous or if it can be interpreted in multiple ways. Provide a score from 0 to 10 based on the following scale:
* 9–10: Completely clear, unambiguous.  
* 6–8: Slight ambiguity, easy to clarify.  
* 3-5: Ambiguous, requires interpretation. 
* 0–2: Highly unclear or confusing.  

3. txt_qa_structure (QA structure): Evaluate the structure of the question and answer pair. Determine if the question is clear and if the answer directly addresses it. Provide a score from 0 to 10 based on the following scale:
* 9–10: Perfect format, concise and clear.  
* 6–8: Slightly verbose but still structured. 
* 3-5: Format is unclear or mismatched.  
* 0–2: Off-topic or incorrect format. 

4. Syntactic_complexity: Assess the structural complexity of the question. Provide a score from 0 to 10 based on the following scale:
* 9–10: (Very varied, complex): Uses a mix of simple, compound, and complex sentences. Includes multiple layers, subordinate clauses, conditionals, or comparative/enumerative structures.  
* 6–8: (Fairly varied, moderate): Mix of simple and some compound sentences. May include light subordination or basic lists.  
* 3-5: (Low variation, simple): Mostly short simple sentences, repetitive structure.  
* 0-2: (Very simple, poor): Only basic sentence patterns, no variety, very predictable.

5. Language_naturalness: Evaluate the naturalness of the language used in the text. Determine if it sounds like natural, fluent Vietnamese or if it is awkward or unnatural. Provide a score from 0 to 10 based on the following scale:
* 9–10 (Very natural, flexible): Conversational tone, fluid sentence flow, no rigid patterns.  
* 6–8 (Quite natural): Mostly natural with occasional formal or stiff phrasing.  
* 3–5 (Less natural, patterned): Monotonous, uses fixed templates. 
* 0–2 (Very unnatural): Rigid, mechanical, unnatural wording.  
"""

VISUAL_QUESTION_ANSWER_CORRELATION = """
You are a system that evaluates the correlation between an image and a text (including a question and a list of answers).

Your task:
1. Analyze the image to extract relevant information.
2. Evaluate each answer **individually** as follows:
    - Check if the question mentions elements present in the image.
    - Check if each answer refers to elements in the image.
    - Check if each answer logically responds to the question.
    - Judge whether the answer could be reasonably guessed without the image.
    - Assess the reasoning level needed to answer the question.

3. More details:

**question_to_image**  
**Goal:** Determine whether the question refers to objects that exist in the image.  
**Response:** yes / no  
**Reason:** Why did you give this assessment? You may provide analysis.
  Basically you have to explain the following elements:
    * Image analysis: What are the main objects and relationships in the image? List them clearly.
    * Question breakdown: What is the question asking about? Identify all mentioned entities and relations.
    * Comparison: For each entity/relation in the question, does it clearly appear in the image? Explain.
    * Final judgment: Based on the above, why is your answer yes or no?
  In addition, you must give detailed reasons and other evidence if any.
---

**answer_to_image**  
**Goal:** Determine whether the elements mentioned in the answers exist in the image.  
Rule: If more than 50% of the answers include elements that do *not* appear in the image, return **no**. Otherwise, return **yes**.  
**Response:** yes / no  
**Reason:** Why did you give this assessment? You may provide analysis.
  Basically you have to explain the following elements:
    * Does it refer to objects or actions in the image?
    * If not, explain what's missing or inconsistent.
    * Count: How many answers are unsupported by the image?
    * Final rule application: Since more than 50% [do / do not] match, answer is yes / no.
  In addition, you must give detailed reasons and other evidence if any.

---

**question_to_answer**  
**Goal:** Assess the correctness of the answer in relation to the question.  
Rule: If more than 50% of the answers do *not* satisfy the question, return **no**. Otherwise, return **yes**.  
**Response:** yes / no  
**Reason:** Why did you give this assessment? You may provide analysis.
  Basically you have to explain the following elements:
    * The question's demand (what it asks for).
    * Check each answer against that demand.
    * List mismatches or violations.
    * Decision logic: If more than 50% of answers violate the question's intent, return no. Otherwise, yes.
  In addition, you must give detailed reasons and other evidence if any.
---

**guess_the_answer**  
**Goal:** Without the image, can the answer to the question be reasonably guessed?  
**Response:** yes / no  
**Reason:** Why did you give this assessment? You may provide analysis.
  Basically you have to explain the following elements:
    * Is the question relying on visual content (e.g. colors, positions, interactions)?
    * Could a reasonable human guess the answer from common sense or stereotypes?
    * Example: “What color is the sky?” → likely yes. “What is the person holding?” → likely no.
    * Conclusion and justification.
  In addition, you must give detailed reasons and other evidence if any.

---

**Reason_depth**  
**Goal:** Assess the required cognitive depth for answering the question.  
**Levels:**

- **Level 1 (Recognition):** Questions about basic object or attribute recognition.  
- **Level 2 (Spatial & Relational):** Reasoning about spatial relationships or attribute comparisons.  
- **Level 3 (Compositional):** Multi-step logical reasoning involving multiple objects and relationships.  
- **Level 4 (Commonsense & Causal):** Requires common knowledge, inference of intentions, mental states, or causality.  
- **Level 5 (Text-in-Image):** Requires reading and interpreting textual content within the image.

**Response:** 1 to 5  
**Reason:** Why did you assign this level? You may provide analysis. In addition, you must give detailed reasons and other evidence if any.
"""

COMBINED_EVALUATION_TEMPLATE = Template(
    """
You are an expert system for comprehensive evaluation of images and accompanying text (questions and answers). Your task is to perform the following four types of evaluations on the provided image, question, and answers, and return all results in a single, unified JSON object.
Note: The question and answers are written in Vietnamese.   
---

## 1. Image Quality Evaluation

${EVALUATE_IMAGE_PROMPT_CONTENT}

---

## 2. Image Diversity Evaluation

${IMAGE_DIVERSITY_PROMPT_CONTENT}

---

## 3. Text Quality Evaluation (for Question and Answers)

Input:
1. Question: ${question}
2. Answers: ${answers}

${EVALUATE_TEXT_PROMPT_CONTENT}

---

## 4. Visual-Text Correlation Evaluation (for Image, Question, and Answers)

Input:
1. Question: ${question}
2. Answers: ${answers}

${VISUAL_QUESTION_ANSWER_CORRELATION_CONTENT}

---

**IMPORTANT OUTPUT INSTRUCTIONS**:
- THIS IS A STRICT REQUIREMENT: You MUST return ONLY a valid JSON object following EXACTLY the structure, key names, data types, and hierarchy described below (no markdown, no explanation, no surrounding text).
- DO NOT omit any field. DO NOT add any extra fields. DO NOT change key names. DO NOT reorder the top-level keys.
- DO NOT include any Markdown syntax such as ```json or ```
- DO NOT include comments inside the JSON (// ...)
- DO NOT use trailing commas at the end of lists or objects.
- All strings MUST use standard double quotes (").
- Ensure all opening and closing brackets `{}`, `[]` are properly matched.
- The top-level JSON must have the following structure, and the keys must match exactly as specified:

Any output that does not match this format exactly will be rejected by the system. Format correctness is critical.

```json
{
    "image_quality_evaluation": {
        "img_clarity": {
            "Score": integer (0-10),
            "Reason": "string"
        },
        "img_occlusion": {
            "Score": integer (0-10),
            "Reason": "string"
        },
        "img_diff_ability": {
            "Score": integer (0-10),
            "Reason": "string"
        },
        "img_object_density": {
            "Score": integer (0-10)
        },
        "img_interaction_level": {
            "Score": integer (0-10),
            "Reason": "string"
        },
        "img_scene_clutter": {
            "Score": integer (0-10)
        }
    },
    "image_diversity_evaluation": {
        "Img_scene_type": "string",
        "Img_main_object": "string",
        "Image_mainobj_descrip": "string",
        "Cultural_context": "string",
        "Demographic_signals": "string",
        "Scene_typicality_score": integer (1-5)
    },
    "text_quality_evaluation": {
        "txt_grammar": {
            "Score_for_question": integer (0-10),
            "Reason_for_question": "string",
            "Score_for_answers": [score_1, score_2,...,score_n], // list[int]: list of scores for each answer,
            "Reason_for_answers": [reason_1, reason_2, ..., reason_n] // list[str]: list of reasons for each answer
        },
        "txt_unambiguity": {
            "Score_for_question": integer (0-10),
            "Reason_for_question": "string",
            "Score_for_answers": [score_1, score_2,...,score_n], // list[int]: list of scores for each answer,
            "Reason_for_answers": [reason_1, reason_2, ..., reason_n] // list[str]: list of reasons for each answer
        },
        "txt_qa_structure": {
            "Score_for_question": integer (0-10),
            "Reason_for_question": "string",
            "Score_for_answers": [score_1, score_2,..., score_n], // list[int]: list of scores for each answer,
            "Reason_for_answers": [reason_1, reason_2,...reason_n] // list[str]: list of reasons for each answer
        },
        "syntactic_complexity": {
            "Score_for_question": integer (0-10),
            "Reason_for_question": "string",
            "Score_for_answers": [score_1, score_2,...,score_n], // list[int]: list of scores for each answer,
            "Reason_for_answers": [reason_1, reason_2,...,score_n] // list[str]: list of reasons for each answer
        },
        "language_naturalness": {
            "Score_for_question": integer (0-10),
            "Reason_for_question": "string",
            "Score_for_answers": [score_1, score_2,...,reason_n], // list[int]: list of scores for each answer
            "Reason_for_answers": [reason_1, reason_2,...,reason_n], // list[str]: list of reasons for each answer
        }
    },
    "correlation_evaluation": {
        "question_to_image": {
            "response": "Yes" or "No",
            "reason": "string"
        },
        "answer_to_image": {
            "response": [], // list[str]: list of "Yes" or "No" for each answer
            "overall_response": "Yes" or "No", // "Yes" if 50% or more of the values in "response" are "Yes". Otherwise, if the majority (more than 50%) are "No", then the overall_response is "No".
            "reason": [] // list[str]: list of reasons for each answer
        },
        "question_to_answer": {
            "response": [], // list[str]: list of "Yes" or "No" for each answer
            "overall_response": "Yes" or "No", // "Yes" if 50% or more of the values in "response" are "Yes". Otherwise, if the majority (more than 50%) are "No", then the overall_response is "No".
            "reason": [] // list[str]: list of reasons for each answer
        },
        "guess_the_answer": {
            "response": "Yes" or "No",
            "reason": "string"
        },
        "reason_depth": {
            "response": integer,
            "reason": "string"
        }
    }
}
* Note: The keys in the final JSON object must match exactly with the keys specified above, and the values must be structured as described. Not included any other text or comments. No explanations, no markdown, no code fences.  
"""
)
