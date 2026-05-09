from flask import Flask, render_template, request

app = Flask(__name__)

# CERTAINTY FACTOR PAKAR
mb = {
    "G1": 0.8,
    "G2": 0.6,
    "G3": 0.5,
    "G4": 0.7,
    "G5": 0.9,
    "G6": 1.0
}

# FORWARD CHAINING
def determine_gejala(g1, g2, g3, g4, g5, g6):

    # RULE BERAT
    if g6 > 0:
        return "Berat"
    if g5 > 0 and (g1 > 0 or g2 > 0 or g3 > 0):
        return "Berat"

    # RULE SEDANG
    if g4 > 0 and g5 == 0:
        return "Sedang"
    if g5 > 0 and g1 == 0 and g2 == 0 and g3 == 0:
        return "Sedang"

    # RULE RINGAN
    return "Ringan"

def determine_riwayat(r1, r2):

    if r1 == "pernah" or r2 == "pernah":
        return "Not_Ok"

    return "Ok"

def determine_diagnosa(gejala, riwayat):

    rule_used = ""
    solusi = ""

    if gejala == "Ringan" and riwayat == "Ok":
        rule_used = "Rule 1"
        diagnosa = "Masalah Perangkat Pengguna"
        solusi = "Restart perangkat, update driver WiFi, lalu reconnect WiFi."

    elif gejala == "Ringan" and riwayat == "Not_Ok":
        rule_used = "Rule 2"
        diagnosa = "Masalah Konfigurasi Jaringan"
        solusi = "Periksa DNS, ubah IP ke DHCP, dan reset konfigurasi jaringan."

    elif gejala == "Sedang" and riwayat == "Ok":
        rule_used = "Rule 3"
        diagnosa = "Masalah Router / Access Point"
        solusi = "Restart router dan cek firmware router."

    elif gejala == "Sedang" and riwayat == "Not_Ok":
        rule_used = "Rule 4"
        diagnosa = "Gangguan ISP Ringan"
        solusi = "Hubungi ISP atau gunakan DNS alternatif."

    elif gejala == "Berat" and riwayat == "Ok":
        rule_used = "Rule 5"
        diagnosa = "Kerusakan Hardware"
        solusi = "Periksa modem/router dan pertimbangkan penggantian perangkat."

    elif gejala == "Berat" and riwayat == "Not_Ok":
        rule_used = "Rule 6"
        diagnosa = "Gangguan ISP Masif"
        solusi = "Tunggu perbaikan ISP atau laporkan ke provider."

    else:
        diagnosa = "Tidak Diketahui"
        solusi = "-"
        rule_used = "-"

    return diagnosa, solusi, rule_used

# CERTAINTY FACTOR
def combine_cf(cf_list):
    if not cf_list:
        return 0
    result = cf_list[0]

    for cf in cf_list[1:]:
        result = result + cf * (1 - result)
    return result

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diagnose', methods=['POST'])
def diagnose():

    # Ambil input user
    g1 = float(request.form.get('G1'))
    g2 = float(request.form.get('G2'))
    g3 = float(request.form.get('G3'))
    g4 = float(request.form.get('G4'))
    g5 = float(request.form.get('G5'))
    g6 = float(request.form.get('G6'))

    r1 = request.form.get('R1')
    r2 = request.form.get('R2')

    # HITUNG CF
    cf_values = []
    if g1 > 0:
        cf_values.append(g1 * mb["G1"])
    if g2 > 0:
        cf_values.append(g2 * mb["G2"])
    if g3 > 0:
        cf_values.append(g3 * mb["G3"])
    if g4 > 0:
        cf_values.append(g4 * mb["G4"])
    if g5 > 0:
        cf_values.append(g5 * mb["G5"])
    if g6 > 0:
        cf_values.append(g6 * mb["G6"])
    final_cf = combine_cf(cf_values)

    # INFERENSI
    gejala = determine_gejala(g1, g2, g3, g4, g5, g6)
    riwayat = determine_riwayat(r1, r2)
    diagnosa, solusi, rule_used = determine_diagnosa(gejala, riwayat)
    confidence = round(final_cf * 100, 2)

    return render_template(
        'result.html',
        diagnosa=diagnosa,
        confidence=confidence,
        gejala=gejala,
        riwayat=riwayat,
        solusi=solusi,
        rule_used=rule_used,
        cf_values=cf_values
    )

if __name__ == '__main__':
    app.run(debug=True)