# LittleFS-SPIFFS Partition Manager v0.3.4

Rövid, Windows alatt futtatható Python/Tkinter segédprogram ESP32 rádiók LittleFS/SPIFFS fájlrendszerének kezeléséhez soros karbantartó protokollon keresztül.<br> 
Az ESP32 szoftverét fel kell készíteni a használatához!<br>
Telepített Python környezetben futtasd a .py fájlt. Ez működik Linux alatt is!<br>
Ha a fenti környezet nincs telepítve, használd az .exe fájlt, ez tartalmazza a futtatási környezetet is!<br>

## Fő funkciók

- COM port kiválasztása és karbantartó mód indítása.
- A rádió fájlrendszerének listázása fa nézetben.
- Teljes fájlrendszer mentése ZIP fájlba.
- ZIP mentés visszaállítása a rádióra.
- Kijelölt fájl mentése PC-re.
- Fájlok és teljes mappák feltöltése várósoron keresztül.
- Kijelölt fájlok vagy mappák törlése.
- Új mappa létrehozása és rádió újraindítása.
- HU/EN felület, sötét Windows témához igazodó megjelenés.

## Mentés és visszaállítás

A teljes mentés ZIP formátumban készül. A program a rádióról olvasott fájlokat az eredeti útvonalukkal menti, beleértve a mappaszerkezetet is.

Egyes firmware-ek a mappában lévő fájlokat csak fájlnévként listázzák, például a `/fonts/test_17.vlw` helyett `test_17.vlw` formában. A program ezt ismert myRadio erőforrásoknál javítja: a `.vlw` fontfájlokat automatikusan a `/fonts` mappához rendeli, így a ZIP mentésben is a megfelelő helyre kerülnek.

Visszaállításkor a ZIP tartalma kerül feltöltésre a rádió fájlrendszerére, a szükséges szülőmappák létrehozásával.

## Feltöltési várósor

A fájlok és mappák először a feltöltési várósorba kerülnek. A várósor indításakor a program egymás után tölti fel az elemeket, közben mutatja:

- aktuális fájl,
- fájlszám,
- sebesség,
- becsült hátralévő idő,
- összesített folyamat,
- hibák száma.

Írási hibánál rövid automatikus újrapróbálkozás történik. Kritikus fájlrendszer-írási hiba esetén a várósor leáll, hogy ne sérüljön tovább a fájlrendszer.

## Törlés

A törlés fájlokra és mappákra is működik. Mappa törlésekor a program először a benne lévő fájlokat törli, majd a mappát. A művelet végén újralistázással ellenőrzi, hogy a kijelölt útvonal valóban eltűnt-e.

A `/fonts` mappa és a `.vlw` fontok kezelése külön figyelmet kap, mert több firmware a fontfájlok szülőmappáját nem jelenti vissza pontosan. A program a megjelenítéshez, mentéshez és törlési ellenőrzéshez ugyanazt az útvonal-javító logikát használja.

## Értesítések

Az általános információs, figyelmeztető és hibaüzenetek saját modális ablakban jelennek meg, a főprogram ablakán belül középre igazítva. Így nem kerülnek más alkalmazások mögé vagy a felhasználói felülettől távolra.

## Követelmények

- Python 3
- `pyserial`
- Windows alatt ajánlott futtatni

Telepítés:

```bash
python -m pip install pyserial
```

Indítás:

```bash
python LittleFS-SPIFFS_Partition_Manager_v0.3.4.py
```

## Megjegyzés

A program a rádió firmware-ének karbantartó protokolljára épül. Ha a firmware eltérően listázza vagy kezeli a fájlokat, a program több ismert esetet javít, de hardveres teszt mindig javasolt mentés, visszaállítás és tömeges törlés előtt.
