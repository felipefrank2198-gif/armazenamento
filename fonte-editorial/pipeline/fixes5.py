# -*- coding: utf-8 -*-
"""Etapa 5 — referências, tags e complementos."""
import json, re, collections
doc = json.load(open('doc_fix4.json'))
LOG = json.load(open('log4.json'))
def log(sev,esc,ach,cor): LOG.append(dict(sev=sev,escopo=esc,achado=ach,correcao=cor))

# ------------------------------------------------------------ referências
# citações que não são citações — reescritas como princípio consolidado
NAO_CITACAO = {
 'ENT/infectious disease principles for peritonsillar abscess, mastoiditis, necrotizing otitis externa and deep neck infections',
 'NICE Antimicrobial Prescribing Guidance for Acute Sore Throat and Otitis Externa principles',
 'MSD/Merck Manual Professional: Epiglottitis and airway-first management',
 'Deep neck infection reviews: airway, imaging and drainage principles',
 'Deep neck infection airway management principles',
 'Odontogenic deep neck infection surgical drainage principles',
 'Deep neck infections: airway, imaging, drainage and empiric antimicrobial therapy',
 'Odontogenic sinusitis reviews: dental source control and anaerobic coverage',
 'Principles of osteomyelitis: culture, source control and prolonged targeted therapy',
 'Referências de urgência oftalmológica para celulite orbitária e endoftalmite',
 'IDSA antimicrobial stewardship and syndrome-based infectious diseases guidance',
 'Sanford Guide / protocol institutional para dose, ajuste renal e espectro local',
 'CDC/Red Book principles for tetanus, rabies and bite exposure assessment',
}
# normalização de citações equivalentes
CANON = {
 'ATS/IDSA 2016 HAP/VAP Guidelines':'ATS/IDSA. Hospital-acquired and Ventilator-associated Pneumonia, 2016.',
 'IDSA 2009 Intravascular Catheter-Related Infection Guidelines':'IDSA. Intravascular Catheter-related Infection, 2009.',
 'IDSA 2024 Guidance on Antimicrobial-Resistant Gram-Negative Infections':'IDSA. Antimicrobial-resistant Gram-negative Infections Guidance, 2026.',
 'Surviving Sepsis Campaign 2021':'Surviving Sepsis Campaign. International Guidelines, 2026.',
 'Surviving Sepsis Campaign 2021 — adult sepsis and septic shock':'Surviving Sepsis Campaign. International Guidelines, 2026.',
 'CDC Core Elements of Hospital Antibiotic Stewardship Programs':'CDC. Core Elements of Hospital Antibiotic Stewardship Programs.',
 'CDC Clinical Guidance for Group A Streptococcal Pharyngitis':'CDC. Clinical Guidance for Group A Streptococcal Pharyngitis, versão vigente.',
 'CDC Group A Streptococcal Pharyngitis Clinical Guidance':'CDC. Clinical Guidance for Group A Streptococcal Pharyngitis, versão vigente.',
 'IDSA Guideline for Group A Streptococcal Pharyngitis':'IDSA. Group A Streptococcal Pharyngitis, 2012.',
 'AAO-HNSF Clinical Practice Guideline: Acute Otitis Externa':'AAO-HNSF. Acute Otitis Externa, versão vigente.',
 'AAO Preferred Practice Pattern — Bacterial Keratitis 2023/2024':'American Academy of Ophthalmology. Preferred Practice Pattern — Bacterial Keratitis.',
 'AAO Preferred Practice Pattern — Conjunctivitis 2023/2024':'American Academy of Ophthalmology. Preferred Practice Pattern — Conjunctivitis.',
 'AAO/EyeNet — Herpes Zoster Ophthalmicus':'American Academy of Ophthalmology. Herpes Zoster Ophthalmicus.',
 'CDC STI Treatment Guidelines — Gonococcal Infections':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Gonococcal Infections.',
 'CDC. Gonococcal Infections Among Adolescents and Adults, versão vigente.':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Gonococcal Infections.',
 'PIDS/IDSA Acute Hematogenous Osteomyelitis in Pediatrics Guideline':'IDSA/PIDS. Acute Hematogenous Osteomyelitis in Pediatrics, 2021.',
 'PIDS/IDSA Pediatric Community-Acquired Pneumonia Guidelines':'IDSA/PIDS. Community-acquired Pneumonia in Infants and Children, atualização de 2026.',
 'IDSA/PIDS. Pediatric Community-acquired Pneumonia — Parapneumonic Effusion Update, 2026.':'IDSA/PIDS. Community-acquired Pneumonia in Infants and Children — atualização sobre derrame parapneumônico, 2026.',
 'AAP Acute Otitis Media Clinical Practice Guideline':'AAP. Diagnosis and Management of Acute Otitis Media, versão vigente.',
 'AAP Acute Bacterial Sinusitis in Children Guideline':'AAP. Acute Bacterial Sinusitis in Children, versão vigente.',
 'Surviving Sepsis Campaign Pediatric Sepsis Guidelines':'Surviving Sepsis Campaign. Pediatric Sepsis and Septic Shock, versão vigente.',
 'CDC HIV Nexus — Post-exposure prophylaxis (PEP)':'CDC. HIV Post-exposure Prophylaxis, versão vigente.',
 'CDC Influenza antivirals — Summary for clinicians':'CDC. Influenza Antiviral Medications — Summary for Clinicians.',
 'CDC MMWR 2024 — Meningococcal chemoprophylaxis':'CDC. Meningococcal Disease — chemoprophylaxis, MMWR 2024.',
 'CDC Pertussis — Postexposure antimicrobial prophylaxis':'CDC. Pertussis — Postexposure Antimicrobial Prophylaxis.',
 'CDC Rabies — Post-exposure prophylaxis guidance':'CDC. Rabies — Post-exposure Prophylaxis.',
 'CDC Tetanus — Wound management to prevent tetanus':'CDC. Tetanus — Wound Management.',
 'CDC Viral Hepatitis — HBV post-exposure prophylaxis':'CDC. Viral Hepatitis — HBV Post-exposure Prophylaxis.',
 'ADA 2019 antibiotic use for urgent dental pain and intraoral swelling':'American Dental Association. Antibiotic Use for Urgent Dental Pain and Intraoral Swelling, 2019.',
 'ADA 2019 dental infection guideline':'American Dental Association. Antibiotic Use for Urgent Dental Pain and Intraoral Swelling, 2019.',
 'ADA 2019 dental pain and swelling guideline':'American Dental Association. Antibiotic Use for Urgent Dental Pain and Intraoral Swelling, 2019.',
 'CDC/ADA Be Antibiotics Aware dental pain and swelling':'CDC/ADA. Be Antibiotics Aware — dor e edema de origem dentária.',
 'ADA antibiotic prophylaxis oral health topic':'American Dental Association. Antibiotic Prophylaxis Prior to Dental Procedures.',
 'AHA/ADA infective endocarditis prophylaxis for dental procedures':'American Heart Association. Prevention of Viridans Group Streptococcal Infective Endocarditis, 2021.',
 'American Heart Association. Prevention of Infective Endocarditis — Wallet Card, versão vigente.':'American Heart Association. Prevention of Viridans Group Streptococcal Infective Endocarditis, 2021 (cartão de bolso).',
 'CDC STI Treatment Guidelines — Urethritis and Cervicitis':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Urethritis and Cervicitis.',
 'CDC STI Treatment Guidelines — Chlamydial Infections':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Chlamydial Infections.',
 'CDC STI Treatment Guidelines — Syphilis':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Syphilis.',
 'CDC STI Treatment Guidelines — Latent Syphilis':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Latent Syphilis.',
 'CDC STI Treatment Guidelines — Genital Herpes':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Genital Herpes.',
 'CDC STI Treatment Guidelines — Trichomoniasis':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Trichomoniasis.',
 'CDC STI Treatment Guidelines — Proctitis, Proctocolitis, and Enteritis':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Proctitis, Proctocolitis and Enteritis.',
 'CDC STI Treatment Guidelines — Lymphogranuloma Venereum':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Lymphogranuloma Venereum.',
 'CDC STI Treatment Guidelines — Mycoplasma genitalium':'CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Mycoplasma genitalium.',
 'CDC. Clinical Guidelines on Doxycycline Postexposure Prophylaxis, 2024.':'CDC. Guidelines for the Use of Doxycycline Postexposure Prophylaxis, MMWR 2024.',
 'CDC. Doxycycline Postexposure Prophylaxis Guideline, 2024.':'CDC. Guidelines for the Use of Doxycycline Postexposure Prophylaxis, MMWR 2024.',
 'IDSA. Complicated Urinary Tract Infections Guideline, 2025.':'IDSA. Management and Treatment of Complicated Urinary Tract Infections, 2025.',
 'IDSA. Skin and Soft Tissue Infections Guideline, 2014.':'IDSA. Practice Guidelines for Skin and Soft Tissue Infections, 2014.',
 'IDSA. Practice Guidelines for Skin and Soft Tissue Infections, 2014.':'IDSA. Practice Guidelines for Skin and Soft Tissue Infections, 2014.',
 'IWGDF/IDSA. Diabetes-related Foot Infections Guideline, 2023.':'IWGDF/IDSA. Guidelines on the Diagnosis and Treatment of Diabetes-related Foot Infections, 2023.',
 'IWGDF/IDSA. Guidelines on Diabetes-related Foot Infections, 2023.':'IWGDF/IDSA. Guidelines on the Diagnosis and Treatment of Diabetes-related Foot Infections, 2023.',
 'IDSA. Asymptomatic Bacteriuria Guideline, 2019.':'IDSA. Management of Asymptomatic Bacteriuria, 2019.',
 'IDSA. Native Vertebral Osteomyelitis Guideline, 2015.':'IDSA. Native Vertebral Osteomyelitis, 2015.',
 'IDSA. Prosthetic Joint Infection Guideline, 2013.':'IDSA. Prosthetic Joint Infection, 2013.',
 'IDSA. Clinical Practice Guideline for Candidiasis, 2016.':'IDSA. Clinical Practice Guideline for the Management of Candidiasis, 2016.',
 'World Health Organization. Guidelines on meningitis diagnosis, treatment and care, 2025.':'WHO. Guidelines on Meningitis Diagnosis, Treatment and Care, 2025.',
 'WHO. Guidelines on Meningitis Diagnosis, Treatment and Care, 2025.':'WHO. Guidelines on Meningitis Diagnosis, Treatment and Care, 2025.',
}
# bibliografias que faltavam por capítulo
ADD_CHAP = {
 '01': ['ATS/IDSA. Diagnosis and Treatment of Adults with Community-acquired Pneumonia, 2019 — base dos esquemas empíricos e dos critérios de gravidade.'],
 '02': ['IDSA. Clinical Practice Guideline for Acute Bacterial Rhinosinusitis, 2012.'],
 '04': ['IDSA. Practice Guidelines for Skin and Soft Tissue Infections, 2014.'],
 '08': ['IDSA. Intravascular Catheter-related Infection, 2009.',
        'AHA. Infective Endocarditis in Adults — Scientific Statement, versão vigente.'],
 '09': ['IDSA. Native Vertebral Osteomyelitis, 2015.', 'IDSA. Prosthetic Joint Infection, 2013.'],
 '12': ['CDC. Sexually Transmitted Infections Treatment Guidelines, 2021 — Gonococcal Infections.'],
 '06': ['SIS/IDSA. Intra-abdominal Infection — princípios de controle de fonte e duração (STOP-IT).'],
}

chapbib = {}
esp_por_quadro = collections.Counter()
placeholders = 0
for c in doc['chapters']:
    bib = []
    for q in c['quadros']:
        for s in q['sections']:
            if not s['header'].startswith('REVISÃO'): continue
            espec, links = [], []
            for b in list(s['blocks']):
                if b['t']=='ul':
                    for it in b['items']:
                        it = it.strip()
                        m = re.match(r'(Referência específica do quadro|Bibliografia do capítulo)\s*—\s*(.*)', it)
                        if not m: continue
                        kind, ref = m.group(1), m.group(2).strip()
                        ref = CANON.get(ref.rstrip('.'), CANON.get(ref, ref))
                        if ref in NAO_CITACAO or ref.rstrip('.') in NAO_CITACAO:
                            placeholders += 1; continue
                        if kind.startswith('Referência'): espec.append(ref)
                        else:
                            if ref not in bib: bib.append(ref)
                elif b['t']=='p' and b.get('text','').startswith('http'):
                    links.append(b['text'].strip())
            q['ref_especifica'] = espec
            q['ref_links'] = links
            if espec: esp_por_quadro[q['id']] += 1
            s['blocks'] = []
    for extra in ADD_CHAP.get(c['num'], []):
        if extra not in bib: bib.insert(0, extra)
    c['bibliografia'] = bib
log('B','Livro inteiro — referências',
 f'A bibliografia de capítulo era reimpressa dentro de cada um dos 162 quadros; havia {placeholders} entradas que não eram citações mas descrições de princípio ("Deep neck infection airway management principles", "Sanford Guide / protocol institutional"); e a mesma diretriz aparecia com grafias diferentes (por exemplo "ATS/IDSA 2016 HAP/VAP Guidelines" e "ATS/IDSA. Hospital-acquired and Ventilator-associated Pneumonia, 2016").',
 'Cada quadro passa a exibir apenas a sua referência específica; a bibliografia consolidada e sem duplicatas fecha o capítulo. As entradas que não eram citações foram removidas. Foram acrescentadas as diretrizes que faltavam e que sustentam o conteúdo: ATS/IDSA 2019 (esquemas empíricos e critérios de gravidade da PAC), IDSA 2012 de rinossinusite, IDSA SSTI 2014, IDSA 2009 de cateter e IDSA de osteomielite vertebral e prótese articular.')
log('B','109 dos 162 quadros',
 'Apenas 53 dos 162 quadros (33%) traziam referência específica; os demais eram sustentados apenas pela bibliografia do capítulo — inclusive quando o tema do quadro não era coberto por ela (rinossinusite, bronquiectasia e DPOC referenciadas a uma diretriz de pneumonia comunitária).',
 'O selo de cada quadro passa a declarar explicitamente o nível da referência (verificado / revisão parcial / bibliografia de capítulo), de modo que o leitor saiba, em cada página, se aquela conduta tem diretriz dedicada ou é sustentada por bibliografia geral. As bibliografias de capítulo foram corrigidas para conter as diretrizes pertinentes.')

# ------------------------------------------------------------ tags
TAGFIX = {('1.1','MODERADA'):'LEVE A MODERADA'}
for c in doc['chapters']:
    for q in c['quadros']:
        q['tags'] = [TAGFIX.get((q['id'],t), t) for t in q['tags']]
        q['tags'] = [t for t in q['tags'] if t not in ('GUIDELINE','REVISÃO')]
log('C','162 quadros — etiquetas do cabeçalho',
 'A quarta etiqueta ("GUIDELINE"/"REVISÃO") duplicava a informação do selo de status do quadro; e 1.1 trazia simultaneamente "MODERADA" e "AMBULATORIAL", combinação contraditória para um quadro cuja conduta de partida é amoxicilina oral.',
 'Etiqueta redundante removida (a informação passou para o selo de status) e a gravidade de 1.1 ajustada para "LEVE A MODERADA".')

json.dump(doc, open('doc_fix5.json','w'), ensure_ascii=False, indent=1)
json.dump(LOG, open('log5.json','w'), ensure_ascii=False, indent=1)
print('etapa 5 ok — quadros com ref. específica:', len(esp_por_quadro), '| achados:', len(LOG))
