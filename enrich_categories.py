#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# Define the notes for each category based on entry types
COLLOCATIONS_NOTES = {
    "결정을 내리다": "Collocate: 결정 + 내리다. Related: 결론을 내리다 (reach conclusion), 선택을 하다 (make choice).",
    "조치를 취하다": "Formal collocation in administrative/policy contexts. Related: 대책을 세우다, 조처를 하다.",
    "책임을 지다": "Common in business/legal contexts. Related: 책임을 져야 하다, 책임감.",
    "결론을 내리다": "Pair with 결정을 내리다. Related: 논점을 정리하다, 결과를 도출하다.",
    "결심을 굳히다": "Emotional commitment verb. Related: 마음을 먹다, 다짐하다.",
    "행동에 옮기다": "Transition from planning to execution. Related: 실행하다, 실천하다.",
    "대책을 세우다": "Policy/planning context. Related: 조치를 취하다, 계획을 세우다.",
    "발판을 마련하다": "Building foundation for future. Related: 기반을 다지다, 토대를 마련하다.",
    "계획을 세우다": "General planning. Related: 목표를 세우다, 전략을 짜다.",
    "목표를 세우다": "Goal-setting. Related: 계획을 세우다, 계획안을 마련하다.",
    "화를 삭이다": "Emotional control. Related: 감정을 추스르다, 마음을 진정시키다.",
    "감정을 추스르다": "Composing oneself. Related: 화를 삭이다, 감정을 가다듬다.",
    "눈물을 참다": "Physical/emotional restraint. Related: 울음을 참다, 감정을 억누르다.",
    "마음을 먹다": "Resolute intention. Related: 결심을 굳히다, 결단을 내리다.",
    "한숨을 쉬다": "Expressing tiredness/frustration. Related: 한숨을 내쉬다, 탄식하다.",
    "속을 끓이다": "Internal worry/agitation. Related: 속이 타다, 마음이 타다.",
    "울분을 토하다": "Venting accumulated frustration. Related: 분노를 표출하다, 울분을 품다.",
    "용기를 내다": "Mustering strength. Related: 용기를 내다, 용감하게 행동하다.",
    "마음을 잡다": "Regaining composure. Related: 정신을 차리다, 집중력을 되찾다.",
    "기분을 풀다": "Cheering up/reconciliation. Related: 기분을 전환하다, 화해하다.",
    "실력을 쌓다": "Skill building (long-term). Related: 경력을 쌓다, 경험을 쌓다.",
    "경력을 쌓다": "Career development. Related: 실력을 쌓다, 경험을 쌓다.",
    "자리를 잡다": "Establishing position/stability. Related: 자리를 차지하다, 정착하다.",
    "야근을 하다": "Working overtime. Related: 초과 근무, 밤새우다.",
    "사표를 내다": "Submitting resignation. Related: 퇴직하다, 회사를 그만두다.",
    "성과를 거두다": "Achievement/results. Related: 성공을 거두다, 결과를 얻다.",
    "일을 맡다": "Taking on responsibility. Related: 역할을 담당하다, 책임을 지다.",
    "직장을 구하다": "Job hunting. Related: 취업하다, 일자리를 찾다.",
    "인정을 받다": "Recognition. Related: 평가를 받다, 주목을 받다.",
    "실수를 만회하다": "Error recovery. Related: 실수를 보완하다, 만회하다.",
}

COLLOQUIAL_NOTES = {
    "헐": "Shock/disbelief exclamation. Younger generation, casual. Related: 정말?, 진짜?.",
    "아이고": "Versatile exclamation for frustration/pain/sympathy. Cross-generational. Related: 아이고머니, 아유.",
    "어머": "Surprise (slightly feminine). Related: 어머나, 오마이갓.",
    "세상에": "Strong surprise. Related: 세상에 다신, 천만의 말씀.",
    "말도 안 돼": "Expressing absurdity. Related: 그럴 리가, 웬일이야.",
    "웬일이야": "Asking what's the occasion. Related: 뭐 하는 거야?, 왜 그래?",
    "그럴 리가": "Disbelief. Related: 말도 안 돼, 있을 수 없지.",
    "어쩜 이렇게": "Expressing amazement. Related: 어떻게 이럴 수 있어, 정말 대단해.",
    "뭐야 이게": "Confusion/disgust. Related: 이게 뭐 하는 거야?, 이건 너무해.",
    "어이가 없다": "Dumbfounded. Related: 황당하다, 코웃음이 나오다.",
}

VERBS_NOTES = {
    "추론하다": "To infer; deduce logically. Used in analytical/academic contexts. Related: 유추하다, 분석하다.",
    "간파하다": "To see through deception/truth. Related: 꿰뚫다, 파악하다.",
    "숙고하다": "To deliberate deeply before major decision. More formal than 생각하다. Related: 검토하다, 고민하다.",
    "반추하다": "To reflect/ruminate on past. Related: 곱씹다, 성찰하다.",
    "탐구하다": "To explore/investigate deeply. Academic context. Related: 연구하다, 조사하다.",
    "사색하다": "To contemplate; meditate. Literary tone. Related: 명상하다, 생각에 잠기다.",
    "변별하다": "To distinguish/differentiate. Formal. Related: 구분하다, 분별하다.",
    "착안하다": "To hit upon idea from inspiration. Related: 착각하다, 아이디어를 얻다.",
    "응용하다": "To apply theory/knowledge practically. Related: 활용하다, 적용하다.",
    "유추하다": "To analogize; extrapolate. Related: 추론하다, 예상하다.",
    "사무치다": "To pierce emotionally; cut deep. Poetic. Related: 애절하다, 마음이 아프다.",
}

ADJECTIVES_NOTES = {
    "까칠하다": "Prickly/irritable personality. Informal but expressive. Related: 까칠까칠하다, 까칠대다.",
    "다소곳하다": "Demure; gently reserved. Literary/formal. Related: 조용하다, 순종적이다.",
    "도도하다": "Aloof; proudly elegant. Related: 거만하다, 고고하다.",
    "싹싹하다": "Friendly; sociable and accommodating. Related: 다정하다, 친절하다.",
    "점잖다": "Dignified; composed propriety. Formal register. Related: 고상하다, 정중하다.",
    "치사하다": "Petty; meanly calculating. Related: 야박하다, 좁은 마음.",
    "너그럽다": "Magnanimous; generously forgiving. Related: 관대하다, 포용적이다.",
    "우직하다": "Stubbornly sincere; straightforward. Related: 성실하다, 직선적이다.",
    "진중하다": "Serious/composed; thoughtfully deliberate. Related: 무거운, 심각한.",
    "교활하다": "Cunning; slyly manipulative. Related: 간사하다, 이중적이다.",
}

ADVERBS_NOTES = {
    "슬쩍": "Sneakily; discreetly so others won't notice. Related: 몰래, 은근히.",
    "넌지시": "Subtly; hinting without being direct. Related: 에돌려, 한번 말씀해.",
    "기꺼이": "Willingly; with genuine pleasure. Related: 흔쾌히, 기쁘게.",
    "거침없이": "Without hesitation; speaking freely. Related: 활발하게, 마음껏.",
    "묵묵히": "Silently; without complaint steadily. Related: 조용히, 말없이.",
    "태연히": "Calmly; nonchalantly maintaining composure. Related: 담담하게, 아무렇지 않게.",
    "서슴없이": "Unhesitatingly; boldly without pause. Related: 거리낌 없이, 과감하게.",
    "빈틈없이": "Flawlessly; thoroughly without gaps. Related: 꼼꼼히, 세밀하게.",
    "고스란히": "Entirely; intact remaining completely. Related: 온전히, 그대로.",
    "더듬더듬": "Fumblingly; haltingly while searching. Related: 어눌하게, 자꾸자꾸.",
}

def extract_and_enrich():
    """Extract 5 categories from vocab.json and enrich with notes."""

    # Read the full vocab.json
    with open('/home/user/korean/data/vocab.json', 'r', encoding='utf-8') as f:
        vocab = json.load(f)

    categories_to_process = [
        ("연어 (Collocations)", "enriched_collocations.json", COLLOCATIONS_NOTES),
        ("구어체 (Colloquial)", "enriched_colloquial.json", COLLOQUIAL_NOTES),
        ("고급 동사 (Advanced Verbs)", "enriched_verbs.json", VERBS_NOTES),
        ("고급 형용사 (Advanced Adjectives)", "enriched_adjectives.json", ADJECTIVES_NOTES),
        ("고급 부사 (Advanced Adverbs)", "enriched_adverbs.json", ADVERBS_NOTES),
    ]

    for category_name, output_filename, notes_dict in categories_to_process:
        if category_name not in vocab:
            print(f"Category '{category_name}' not found in vocab.json")
            continue

        entries = vocab[category_name]
        enriched_entries = []

        for entry in entries:
            enriched_entry = entry.copy()
            korean_word = entry.get("korean", "")

            # Add notes if available
            if korean_word in notes_dict:
                enriched_entry["notes"] = notes_dict[korean_word]
            else:
                # Fallback: generate a simple note
                if "notes" not in enriched_entry:
                    enriched_entry["notes"] = "Related concepts and usage variations in natural Korean."

            enriched_entries.append(enriched_entry)

        # Write to output file
        output_path = f'/home/user/korean/data/{output_filename}'
        output_data = {category_name: enriched_entries}

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✓ Created {output_path} with {len(enriched_entries)} enriched entries")

if __name__ == "__main__":
    extract_and_enrich()
    print("\nAll categories enriched and written to separate files!")
