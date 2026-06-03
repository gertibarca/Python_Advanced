from kerrielektrik import KerrElektrik

if __name__ == "__main__":
    kerri = KerrElektrik("Tesla", "E zezë", 2026, "100 kWh")

    kerri.rriteGazin(60)
    kerri.uleGazin(25)

    kerri.setName("Porsche Taycan")
    print(kerri.get_name())