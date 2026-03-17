from backend.WaterSource import WaterSource

class Village:
    VILLAGGIO_A = None
    VILLAGGIO_B = None
    SOGLIA_ACQUA_CRITICA   = 10   # % sotto cui scatta la crisi idrica
    SOGLIA_MORALE_GUERRA   = 40   # % sotto cui si apre l'opzione guerra/pace
    DECREMENTO_MORALE      = 8    # punti morale persi ogni anno in crisi
    RECUPERO_MORALE        = 5    # punti morale recuperati ogni anno fuori crisi
    DECREMENTO_PERSONE_PCT = 3    # % popolazione che muore ogni anno in crisi idrica
    CONSUMO_ACQUA_ANNUO    = 5    # unità d'acqua consumate ogni anno per persona (scalato)


    def __init__(self, nome: str, num_persone: int, morale: int, consumo_acqua: int, riserva_acqua: int):
        self.nome = nome
        self.num_persone = num_persone
        self.morale = morale
        self.consumo_acqua = consumo_acqua
        self.riserva_acqua = riserva_acqua

        self.morti_totali = 0


        if Village.VILLAGGIO_A is None:
            Village.VILLAGGIO_A = self
        else:
            Village.VILLAGGIO_B = self

    # region Proprietà villaggio

    @property
    def in_crisi_idrica(self) -> bool:
        return self.riserva_acqua < self.SOGLIA_ACQUA_CRITICA

    @property
    def in_crisi_morale(self) -> bool:
        return self.morale <= self.SOGLIA_MORALE_GUERRA

    @property
    def estinto(self) -> bool:
        return self.num_persone <= 0

    # region Modifica Parametri

    def modifica_riserva_acqua(self, quantita: int):
        self.riserva_acqua = max(0, min(100, self.riserva_acqua + quantita))

    def avvelena_fonte(self):
        WaterSource.INSTANCE.poisoned = True

    # region Aggiornamenti Annuali

    def modifica_morale(self):
        if self.in_crisi_idrica:
            self.morale = max(0, self.morale - self.DECREMENTO_MORALE)
        else:
            self.morale = min(100, self.morale + self.RECUPERO_MORALE)

    def modifica_num_persone(self):
        if self.in_crisi_idrica and not self.estinto:
            morti = max(1, int(self.num_persone * (self.DECREMENTO_PERSONE_PCT / 100)))
            self.num_persone -= morti
            self.morti_totali += morti

    def consuma_acqua(self):
        if not WaterSource.INSTANCE.poisoned:
            self.modifica_riserva_acqua(-self.consumo_acqua)

    def aggiorna_anno(self, quantita_acqua):
        self.consuma_acqua()
        self.modifica_riserva_acqua(quantita_acqua)
        self.modifica_morale()
        self.modifica_num_persone()

    # region Utiliy

    def stato(self) -> dict:
        return {
            "nome": self.nome,
            "num_persone": self.num_persone,
            "morale": self.morale,
            "riserva_acqua": self.riserva_acqua,
            "in_crisi_idrica": self.in_crisi_idrica,
            "in_crisi_morale": self.in_crisi_morale,
            "morti_totali": self.morti_totali,
        }

    def __repr__(self):
        return (f"Village({self.nome} | persone={self.num_persone} "
                f"| morale={self.morale}% | acqua={self.riserva_acqua}%)")