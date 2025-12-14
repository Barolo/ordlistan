🌟 LEXIQO DESIGN SYSTEM – Style Guide v1.0

En sammanhållen visuell och funktionell riktlinje för hela Lexiqo-plattformen.

📌 1. Brand Identity

Lexiqo är en modern, inspirerande och premium-känsla språkinlärningsplattform.
Stilen ska vara:

Mjukt futuristisk

Lila, djup och pulserande

Vågigt och flow-baserat (inspirerat av språk, rörelse och utveckling)

Ung, men professionell

Trygg och lugn i light mode, vibrerande och rik i dark mode

Den grafiska identiteten bygger på kurvor, gradienter och djup.

🎨 2. Färger
2.1 Primärpalett (Brand Colors)

Dessa färger är centrala för Lexiqos identitet.

Namn	Hex	Användning
Deep Purple	#3A0CA3	Viktigaste färgen. Hero-bakgrunder, dark mode accenter.
Primary Purple	#5A36C8	Brand buttons, länkar, highlights.
Vivid Purple	#8F6BFF	Hover-states, gradients, mjukt ljus.
Soft Lilac	#C7B6FF	Borders, subtila highlights, light mode accenter.
2.2 Neutraler – Light Mode
Namn	Hex	Användning
Background Light	#F7F4FF	Sidbakgrund
Surface Light	#FFFFFF	Cards, paneler
Text Primary	#1A1A1A	Brödtext
Text Secondary	#5A5A5A	Undertext
2.3 Neutraler – Dark Mode
Namn	Hex	Användning
Background Dark	#0D0914	Huvudbakgrund
Surface Dark	#1A1427	Cards, modaler
Text Light	#F2F2F2	Brödtext
Text Muted	#A892D6	Sekundär text
🌈 3. Gradienter & Bakgrunder

Lexiqo använder mjuka vågor och djuplila färger.

3.1 Hero-bakgrund

Rekommenderat:

linear-gradient(
    125deg,
    #3A0CA3 0%,
    #5A36C8 40%,
    #8F6BFF 100%
);

3.2 Vågmönster – “Lexiqo Wave Pattern”

Kurvor ska vara mjuka

Lager ska ha subtila skillnader i luminans

Formen ska ge ett djup utan att bli distraherande

(Filen hero_bg.png fungerar som officiell referens.)

🔤 4. Typografi
4.1 Primär font

Inter

Ren

Modern

Extremt läsbar

Perfekt för UI och textbaserat innehåll

4.2 Dekorativ font

Courgette

Endast för logotyp, rubriker på specifika sidor, brand-calls

Ska användas sparsamt

4.3 Typografisk skala
Element	Storlek	Vikt
H1	48px	700
H2	32px	600
H3	24px	600
Body	16px	400
Small	14px	400
🟪 5. Komponenter
5.1 Buttons

Primary Button

Bakgrund: #5A36C8

Text: #FFFFFF

Radius: 12px

Hover:

Lyft: transform: translateY(-2px)

Färg: ljusare lila

Glow i dark mode

Secondary Button

Vit bakgrund

Lila text

Border: 1px solid #8F6BFF

5.2 Cards

Radius: 16–20px

Light mode: mjuk skugga

Dark mode: lila yttre glow

Ytor ska vara rena och luftiga

5.3 Form Inputs

Radius: 10px

Border: 1px solid #C7B6FF

Focus outline: lila glow

📊 6. Ikoner & Illustrationer

Mjuka geometriska former

Runda hörn

Föredra linjära ikoner i light mode

Föredra fyllda ikoner i dark mode för kontrast

🌓 7. Light Mode & Dark Mode Principer
Light Mode

Mjukt, luftigt, vit bakgrund

Lila ska sticka ut, men inte dominera

Text svärta max 90%

Dark Mode

Djupa purpurtoner

Glow-effekter tillåtna

Viktigt med tillräcklig kontrast

Undvik rena svarta (#000000)

🔧 8. Utveckling & CSS-riktlinjer
8.1 Variabler (CSS Custom Properties)

Skapa i variables.css:

:root {
  --purple-deep: #3A0CA3;
  --purple-primary: #5A36C8;
  --purple-light: #8F6BFF;
  --purple-soft: #C7B6FF;

  --bg-light: #F7F4FF;
  --surface-light: #FFFFFF;

  --bg-dark: #0D0914;
  --surface-dark: #1A1427;
}

8.2 Återanvänd komponenter

Buttons

Cards

Layout-grids

Typografiklasser

8.3 Filstruktur

Rekommenderad:

static/css/
    base/
    components/
    pages/
    themes/

🧪 9. Testning & Konsistens

Alla nya komponenter ska testas i:

Light mode

Dark mode

Desktop (default)

Mobil (små skärmar)

Allt nytt content ska följa:

Färgpaletten

Typografi

Radius-regler

Buttoninteraktioner

🚀 10. Vision framåt

Lexiqo ska kännas:

Som en premium app

Som ett lärande rum

Modern, personlig

UX ska kännas mjukt flytande, precis som språk är

Med denna style guide kan vi säkerställa att:

Alla nya sidor känns enhetliga

Designen skalar

Flera utvecklare kan bidra utan att stil bryts

Dark mode/light mode blir konsekvent