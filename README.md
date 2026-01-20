# Robotbilsprojekt

## De overordnede formål med projektet er at:

- Gennemføre et projekt som involverer fagene
  - Software
  - embedded systems
  - management
  - netværk
- Bygge og programmere robotbilen så den kan deltage i et antal konkurrencer
- Dokumentere og præsentere projektet.

## Tidsplan

| Emne | Underviser og dato |
|---|---|
| Intro til opgaven | KBKJ/LKAA og FIKR 20/01 (Bil dele udleveres)|
| Wbs, critical path og Gannt, gruppekontrakt, projekt initiation |FIKR 22/01, 29/01, 05/02 og 12/02 |
| H-bro (Regulator – LIPO) | LKAA 26/01 |
| Batteri typer | KBKJ 27/01|
|UDP (pico og pc) | LKAA 02/02|
|Struktureret programmering og Klasser i python| FIKR 23/01 & 30/01 & 06/02 & 13/02 & 20/02
| Intro af rapport skabelon | FIKR 19/02|
|Reflektionssensoren |LKAA 09/02|
| Samling af bil| KBKJ 20/01 og 21/01|
|State-maskine| KBKJ 04/02|
|Reguleringsteknik| KBKJ 10/02,17/02|
|TOF-sensor| LKAA 02/02|
| Arbejde m robotbil | Uge 8 23/02 -27/02|
|Konkurrence kørsel i lodde kælderen | LKAA, FIKR 02/03|
|De studerende fremlægger opnåede resultater. (og biler tilbage til afdeling) |LKAA, FIKR 05/03|
|Rapport aflevering | ___06/03___|

## Konkurrencerne
Der bliver afholdt en Wall-follow konkurrence, en SUMO-kamp og en fodbold konkurrence.
Det er et krav at bilen skal kunne deltage i alle tre discipliner
Reglerne for konkurrencerne er som beskrevet herunder
(I tvivlstilfælde er underviserens afgørelser endelig 😊):
### Wall Following:
- Bilen skal kunne køre fremad ved at følge væggen på højre side af bilen (set i bevægelsesretningen). Denne funktion skal udføres autonomt af bilen ved at bruge TOF - lasersensorenheden.
- Der arrangeres tidskørsel for bilerne på en bane.
- Ingen indgriben er tilladt efter bilen er startet
- Der gives point afhængig af hastigheden hvormed banen gennemføres.
- For at opnå en god tid er det vigtigt at robotbilen reagerer passende hurtigt.
- Væggen der skal følges, vil have maximalt 90 graders hjørner(ind og ud).
- Der køres i henhold til elevernes baneudvalgs regler (vedhæftet). Sidste beslutning er hoveddommerens.

### SUMO Battle (autonom konkurrence i at skubbe papkasser ud af en cirkulær arena):

- Ingen indgriben er tilladt efter bilen er startet i SUMO konkurrencen.
- Robotbilen skal bruge de indbyggede sensorer til navigation.
- Arenaen er markeret med sort tape.
- Formålet er at skubbe alle kaserne ud af arenaen.
- Der bliver arrangeret en konkurrence. (tidtagning)
- Der må ikke tilføjes dele, der rækker ud over chassiset
- Der gives point afhængig af antallet af ud-skubbede kasser og den tid der er brugt.

### Fjernstyret fodbold.

- Der skal laves et Python program på Pc’en som kan give brugeren mulighed for at styre robotbilen og dermed deltage i en fodboldkamp.
- Fodboldbanen bliver cirka 4x6 meter med sidevægge
- Målet vil være ca. 1 meter bred i hver ende af banen
- Der vil blive etableret et antal runder af hver cirka 5 minutter. Hver af robotbilerne vil være med i mindst tre runder.
  - NB: Dette program skal også kunne
  - Sætte bilen i Wall-follow-mode og i SUMO-mode
  - Og vise den aktuelle spændingen på batteriet.

## Materialer

### RoboCar-Set
- 1 x Infra-red reflective light sensors QRE1113 or similar
- 1 x TOF light sensor (LT53l1X) GY53
- 1 x 2wd Robot Smart Car Chassis Kits
- 1 x H-bridge. (consult the datasheet)
- 1 x Lithium Ion battery pack for running the car
- Skruer og møtrikker.

> De studerende skal udføre en kvalitetskontrol af de materialer der modtages.
> Det er komponenter som har været anvendt før, så fejl i komponenterne må forventes.

Nye komponenter kan rekvireres ved underviseren. Bilsættene vil også være mere eller mindre samlede i forvejen.

## De faglige formål med projektet er at anvende:

### I managementfaget
- Work break down
- Gantt diagram

### I softwarefaget at
- Lave en løsning som baserer sig på modulstruktur med et funktionshierarki
- Lave stabil og testbar software.
- Dokumentere software med
  - flowchart.
  - input, proces og output
  - test af funktionalitet
- __Hver studerende skal udvikle mindst en softwarefunktion__
- Holdet skal tegne hele modulstruktur med funktionshierarkiet

### I embedded faget
- Tegne et blokdiagram af hele systemet
- Arbejde struktureret på modulniveau
- Tegne et elektrisk diagram af bilen.
- Håndtere
  - Aktuatorer (H-bro, DC-motorer)
  - Sensorer (reflektionssensor, TOF-sensor)
  - Energiforsyningen LiPo batteri
  - De elektriske og mekaniske problemer der opstår i projektet
  - Kommunikationstekniske udfordringer (UDP)

# Krav til rapporten/afleveringen
- Rapporten skal følge afdelingens tekniske rapportskabelon
- Projektrapportens længde skal være mellem 8 og 12 normalsider. (20000 til 30000 anslag)

## Minimum indhold:
- Blok Diagram på systemniveau
- Et elektrisk diagram (retningslinjer fra embedded faget)
- WBS dokumentation
- Gantt diagram
- Flowchart.
- Kildekode for de programmerede moduler (i appendix)
- Link til teknisk video (youtube eller lignende)
- Vedhæft powerpoint eller lignende
- Testcases for projektet

# Krav til præsentationen
> (15 minutter inklusive video og spørgsmål)

Se dette som en eksamenssituation. Så overbevis Underviserne om, at I som gruppe er ansvarlige for og har styr på alle tekniske aspekter af dette projekt. Indholdet i præsentationen skal tage udgangspunkt i reflektioner over en systemforbedring. (find noget som ikke virkede optimalt og fremlæg design til et forbedringsforslag)

Denne præsentation vil være for hele klassen, og hvert gruppemedlem skal deltage aktivt i præsentationen.
Præsentationen skal støttes af en elektronisk præsentation: .pptx,.pdf, link til Prezi
eller andet.

### Video (maximalt 1 minut)
- En teknisk video som dokumenterer at robotbilen kan leve op til kravene.

Reserver 3 minutter til spørgsmål/diskussion med tilhørere.
