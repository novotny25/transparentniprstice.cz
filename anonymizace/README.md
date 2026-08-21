# Anonymizace — jak to funguje lidsky

Tahle složka je pojistka proti tomu, aby se na veřejný web omylem dostalo
něco, co tam nepatří. Není to jen dobrý úmysl — je to pravidlo, které
kontroluje skript a bez kterého se nedá nasadit.

## Odkud kam data tečou

```
SOUKROMÁ ZÓNA (PACT, soukromý repozitář)
│
│  originální účetní export obce
│  – obsahuje jména lidí, adresy, čísla dokladů
│  – nikdy neopustí tuhle zónu
│
▼  skript podle anonymizace/pravidla.yml
│
VEŘEJNÝ REPOZITÁŘ (transparentniprstice.cz)
   nově vytvořené soubory, ve kterých jména a adresy nikdy nebyly
```

Klíčové slovo je **nově vytvořené**. Veřejný soubor nevzniká tak, že se
z originálu něco vymaže. Vzniká tak, že se z originálu vezme jen to, co je
v pravidlech výslovně povolené, a zbytek se nikam nepřenese. Rozdíl je
zásadní: u mazání stačí jedna mezera v pravidle a údaj projde. Tady musí
projít schválením, jinak neprojde vůbec.

## Tři soubory a co dělají

| Soubor | K čemu je |
|---|---|
| `pravidla.yml` | Co smí ven. Seznam povolených polí, seznam zakázaných, vzory pro hledání osobních údajů, postup pro PDF a podmínky publikace. |
| `verejna-allowlist.yml` | Seznam výjimek. Teď je prázdný a je to záměr — nic se neponechává. |
| `cislenik-popisu.yml` | Číselník veřejných označení. Vznikne v úkolu 1.1. |

## Proč je popis zápisu nahrazený, ne vyčištěný

Původní účetní export má u každé položky krátký volný popis. Vypadá
nevinně, ale mezi 509 unikátními popisy jsou i takové, kde je jméno
konkrétního člověka rovnou vedle jeho adresy. V obci o tisíci obyvatelích
stačí i samotná adresa.

Šly by dvě cesty. Buď popis nechat a jména z něj vymazávat, nebo popis
nahradit označením z pevného seznamu. Zvolili jsme druhou — protože
u první cesty se nikdy nedozvíte, co jste přehlédli. Když se popis
nepodaří přiřadit, nepublikuje se v původní podobě: dostane obecné
označení podle kategorie a objeví se v kontrolním reportu.

## Co dělá skript a co člověk

**Skript** najde kandidáty a připraví kontrolní report — všechny zásahy,
všechna nerozhodnutá místa a náhledy všech stran PDF, aby byly vidět
i podpisy a rukopis, na které textové hledání nestačí.

**Petr** projde report v jediné souhrnné kontrole a rozhodne. Nic
nezačerňuje ručně. Opravy se zapíšou do pravidel a výstupy se vygenerují
znovu — takže rozhodnutí platí i pro všechna příští data.

Ani skript, ani AI nejsou samy o sobě zárukou. Proto tu je brána: bez
kontroly PASS, nuly nevyřešených nálezů a Petrova podpisu se necommituje
a nenasazuje.

## Kdyby se něco přesto dostalo ven

Smazat soubor v novém commitu nestačí — v historii gitu zůstane. Postup
je: zastavit nasazení, přepsat historii nebo založit repozitář znovu,
a teprve pak publikovat. Proto se kontrola dělá **před** commitem.
