# Eingabedatei
input_file = "build_words_uncleaned.txt"
output_file = "build_words.txt"

# Datei einlesen
with open(input_file, "r", encoding="utf-8") as f:
    words = f.readlines()

# Leerzeichen und Zeilenumbrüche entfernen
words = [w.strip() for w in words if w.strip()]

# Duplikate entfernen + alphabetisch sortieren (case-insensitive)
unique_sorted = sorted(set(words), key=str.lower)

# Ergebnis speichern
with open(output_file, "w", encoding="utf-8") as f:
    for word in unique_sorted:
        f.write(word + "\n")

print("Fertig! Duplikate entfernt und alphabetisch sortiert.")