# =============================================================================
# ANALISIS ASOSIASI - APRIORI & FP-GROWTH
# Input  : Data diinput manual per kategori (sudah dikoreksi)
# Periode: 2024-06-08 s/d 2026-05-25
# Metode : Apriori dan FP-Growth (via eclat)
# phi (min support count) = 3
# =============================================================================

# ── 0. INSTALL & LOAD PAKET ──────────────────────────────────────────────────
packages <- c("arules", "arulesViz", "dplyr", "tidyr",
              "ggplot2", "stringr", "RColorBrewer")
for (pkg in packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg)
  library(pkg, character.only = TRUE)
}


# =============================================================================
# 1. INPUT DATA MANUAL PER TRANSAKSI
#    Format: setiap elemen list = satu struk belanja
#    Data disajikan langsung dalam kategori produk.
# =============================================================================

transaksi_kategori <- list(
  "1"  = c("Bahan Pokok","Sayuran","Susu & Olahan Susu","Susu & Olahan Susu",
            "Sayuran","Minuman","Bahan Pokok","Bahan Pokok","Bahan Pokok",
            "Susu & Olahan Susu","Mie Instan","Mie Instan","Minuman"),
  "2"  = c("Buah","Snack","Sayuran","Susu & Olahan Susu",
            "Susu & Olahan Susu","Bahan Pokok","Bahan Pokok",
            "Bumbu & Rempah","Sayuran","Ikan & Seafood"),
  "3"  = c("Makanan Instan","Makanan Instan","Makanan Instan",
            "Buah","Bumbu & Rempah","Bumbu & Rempah"),
  "4"  = c("Daging & Olahan","Snack","Bahan Pokok"),
  "5"  = c("Perawatan Tubuh","Sayuran"),
  "6"  = c("Ikan & Seafood","Bumbu & Rempah","Bumbu & Rempah",
            "Bumbu & Rempah","Bumbu & Rempah","Bahan Pokok",
            "Bahan Pokok","Bumbu & Rempah","Sayuran",
            "Sayuran","Bumbu & Rempah","Sayuran",
            "Sayuran","Bumbu & Rempah","Sayuran",
            "Bumbu & Rempah","Bahan Pokok","Bumbu & Rempah",
            "Sayuran","Sayuran","Sayuran"),
  "7"  = c("Susu & Olahan Susu","Minuman","Perawatan Tubuh",
            "Frozen Food","Perawatan Tubuh","Perawatan Tubuh",
            "Perawatan Tubuh","Perawatan Tubuh",
            "Kebersihan Rumah",
            "Perawatan Tubuh"),
  "8"  = c("Buah","Buah","Sayuran","Buah"),
  "9"  = c("Kantong & Tas","Frozen Food","Frozen Food",
            "Makanan Instan","Susu & Olahan Susu","Roti",
            "Susu & Olahan Susu","Sayuran"),
  "10" = c("Minuman","Snack","Perawatan Tubuh","Bahan Pokok",
            "Perawatan Tubuh","Bahan Pokok","Sayuran","Kantong & Tas"),
  "11" = c("Susu & Olahan Susu","Snack","Snack"),
  "12" = c("Perawatan Tubuh","Perawatan Tubuh","Kantong & Tas"),
  "13" = c("Kebersihan Rumah","Kebersihan Rumah","Minuman",
            "Minuman","Bahan Pokok","Buah",
            "Daging & Olahan","Bumbu & Rempah","Bumbu & Rempah",
            "Mie Instan","Daging & Olahan","Bumbu & Rempah",
            "Buah","Ikan & Seafood","Daging & Olahan",
            "Bumbu & Rempah","Bumbu & Rempah"),
  "14" = c("Perawatan Tubuh","Perawatan Tubuh","Kantong & Tas"),
  "15" = c("Minuman","Perawatan Tubuh"),
  "16" = c("Perawatan Tubuh","Perawatan Tubuh","Kebersihan Rumah"),
  "17" = c("Snack","Snack","Snack","Bahan Pokok","Snack","Bahan Pokok"),
  "18" = c("Bahan Pokok","Bahan Pokok"),
  "19" = c("Kantong & Tas","Bumbu & Rempah","Bumbu & Rempah","Bumbu & Rempah",
            "Bumbu & Rempah","Bumbu & Rempah","Snack","Bumbu & Rempah"),
  "20" = c("Frozen Food","Minuman",
            "Kebersihan Rumah",
            "Perawatan Tubuh","Kebersihan Rumah","Kantong & Tas"),
  "21" = c("Bahan Pokok","Bumbu & Rempah","Minuman","Minuman","Bahan Pokok"),
  "22" = c("Snack","Snack","Susu & Olahan Susu","Susu & Olahan Susu",
            "Minuman","Minuman","Kantong & Tas"),
  "23" = c("Minuman","Minuman"),
  "24" = c("Minuman","Snack","Daging & Olahan","Susu & Olahan Susu"),
  "25" = c("Kebersihan Rumah","Kantong & Tas","Makanan Instan",
            "Snack","Snack","Minuman","Susu & Olahan Susu","Kantong & Tas"),
  "26" = c("Daging & Olahan","Daging & Olahan","Daging & Olahan"),
  "27" = c("Kebersihan Rumah","Perawatan Tubuh","Bahan Pokok","Mie Instan"),
  "28" = c("Minuman","Minuman"),
  "29" = c("Mie Instan","Snack","Mie Instan",
            "Snack",
            "Snack","Mie Instan","Roti","Susu & Olahan Susu","Snack"),
  "30" = c("Daging & Olahan","Snack"),
  "31" = c("Snack","Snack","Snack","Snack","Snack",
            "Snack",
            "Bumbu & Rempah",
            "Daging & Olahan",
            "Mie Instan","Mie Instan")
)


# =============================================================================
# 2. RINGKASAN DATA
# =============================================================================
tgl_min     <- as.Date("2024-06-08")
tgl_max     <- as.Date("2026-05-25")
N_TRANSAKSI <- length(transaksi_kategori)
PHI         <- 3
MIN_SUP     <- PHI / N_TRANSAKSI
MIN_CONF    <- 0.5
MIN_LIFT    <- 1.0

cat("=============================================================\n")
cat(" ANALISIS ASOSIASI - APRIORI & FP-GROWTH\n")
cat(" (Input Manual - Kategori Sudah Dikoreksi)\n")
cat("=============================================================\n")
cat(sprintf(" Periode      : %s s/d %s\n", tgl_min, tgl_max))
cat(sprintf(" N transaksi  : %d struk\n", N_TRANSAKSI))
cat(sprintf(" phi          : %d (min support count)\n", PHI))
cat(sprintf(" min_support  : %.4f\n", MIN_SUP))
cat(sprintf(" min_conf     : %.2f\n", MIN_CONF))
cat(sprintf(" min_lift     : %.1f\n", MIN_LIFT))
cat("=============================================================\n\n")


# =============================================================================
# 3. FUNGSI HELPER
# =============================================================================

buat_trans <- function(lst) {
  as(lst, "transactions")
}

ringkasan_rules <- function(rules, label) {
  cat(sprintf("\n--- %s ---\n", label))
  cat(sprintf("  Jumlah rules : %d\n", length(rules)))
  if (length(rules) > 0) {
    top <- head(sort(rules, by = "lift"), 10)
    cat("  Top-10 rules (sort by lift):\n")
    inspect(top)
  }
}

fpgrowth_rules <- function(trans, sup, conf) {
  fi <- eclat(trans,
              parameter = list(supp = sup, minlen = 2, maxlen = 10),
              control   = list(verbose = FALSE))
  if (length(fi) == 0) return(NULL)
  rules <- ruleInduction(fi, trans, confidence = conf)
  rules <- rules[quality(rules)$lift >= MIN_LIFT]
  rules
}

ekspor_rules <- function(rules, nama_file) {
  if (is.null(rules) || length(rules) == 0) {
    cat(sprintf("  [SKIP] %s — tidak ada rules.\n", nama_file)); return(invisible(NULL))
  }
  df_r <- as(rules, "data.frame") %>% arrange(desc(lift))
  write.csv(df_r, nama_file, row.names = FALSE)
  cat(sprintf("  [OK] %s (%d rules)\n", nama_file, nrow(df_r)))
}


# =============================================================================
# 4. LEVEL 1 — PER KATEGORI
# =============================================================================
cat("═══════════════════════════════════════════════════════════\n")
cat(" LEVEL 1: ANALISIS PER KATEGORI\n")
cat("═══════════════════════════════════════════════════════════\n")

trans_kategori <- buat_trans(transaksi_kategori)

rules_apr_kat <- apriori(
  trans_kategori,
  parameter = list(supp = MIN_SUP, conf = MIN_CONF, minlen = 2, maxlen = 10),
  control   = list(verbose = FALSE)
)
rules_apr_kat <- rules_apr_kat[quality(rules_apr_kat)$lift >= MIN_LIFT]
ringkasan_rules(rules_apr_kat, "APRIORI - Per Kategori")

rules_fpg_kat <- fpgrowth_rules(trans_kategori, MIN_SUP, MIN_CONF)
ringkasan_rules(rules_fpg_kat, "FP-GROWTH - Per Kategori")


# =============================================================================
# 6. VISUALISASI
# =============================================================================
pal <- RColorBrewer::brewer.pal(8, "Set2")

## VIZ 1: Frekuensi kategori
png("viz_01_frekuensi_kategori.png", width = 1000, height = 600, res = 120)
itemFrequencyPlot(trans_kategori, topN = 16, type = "absolute", col = pal[1],
  main = sprintf("Frekuensi Kategori per Transaksi\n(%s s/d %s)", tgl_min, tgl_max),
  ylab = "Frekuensi (jumlah transaksi)", xlab = "", cex.names = 0.80, las = 2)
dev.off()

## VIZ 2: Scatter Apriori kategori
if (length(rules_apr_kat) > 0) {
  png("viz_02_scatter_apriori_kategori.png", width = 900, height = 700, res = 120)
  plot(rules_apr_kat, measure = c("support","confidence"), shading = "lift",
    main = sprintf("Scatter - Apriori (Kategori)\nphi=%d | min_conf=%.2f", PHI, MIN_CONF))
  dev.off()
}

## VIZ 3: Graph top-20 rules kategori
if (length(rules_apr_kat) > 0) {
  top_kat <- head(sort(rules_apr_kat, by = "lift"), 20)
  png("viz_03_graph_apriori_kategori.png", width = 1000, height = 900, res = 120)
  plot(top_kat, method = "graph", engine = "igraph")
  title(main = sprintf("Graph Top-20 Rules - Apriori\n%s s/d %s", tgl_min, tgl_max))
  dev.off()
}

## VIZ 4: Graph FP-Growth kategori
if (!is.null(rules_fpg_kat) && length(rules_fpg_kat) > 0) {
  top_fpg <- head(sort(rules_fpg_kat, by = "lift"), 20)
  png("viz_04_graph_fpgrowth_kategori.png", width = 1000, height = 900, res = 120)
  plot(top_fpg, method = "graph", engine = "igraph")
  title(main = sprintf("Graph Top-20 Rules - FP-Growth\n%s s/d %s", tgl_min, tgl_max))
  dev.off()
}

## VIZ 5: Perbandingan jumlah rules
tabel_perbandingan <- data.frame(
  Metode  = c("Apriori","FP-Growth"),
  N_Rules = c(
    length(rules_apr_kat),
    ifelse(is.null(rules_fpg_kat), 0, length(rules_fpg_kat))
  )
)

png("viz_05_perbandingan_metode.png", width = 800, height = 500, res = 120)
print(
  ggplot(tabel_perbandingan, aes(x = Metode, y = N_Rules, fill = Metode)) +
    geom_col(width = 0.6) +
    geom_text(aes(label = N_Rules), vjust = -0.4, size = 4, fontface = "bold") +
    scale_fill_manual(values = c("Apriori" = pal[3], "FP-Growth" = pal[4])) +
    labs(
      title    = "Perbandingan Jumlah Rules - Kategori",
      subtitle = sprintf("Periode: %s s/d %s  |  phi=%d  |  min_conf=%.2f  |  min_lift=%.1f",
                         tgl_min, tgl_max, PHI, MIN_CONF, MIN_LIFT),
      x = "Metode", y = "Jumlah Rules", fill = "Metode"
    ) +
    theme_minimal(base_size = 13) +
    theme(plot.title = element_text(face = "bold"))
)
dev.off()


# =============================================================================
# 7. EKSPOR RULES KE CSV
# =============================================================================
cat("\n[INFO] Ekspor rules ke CSV...\n")
ekspor_rules(rules_apr_kat,    "rules_apriori_kategori.csv")
ekspor_rules(rules_fpg_kat,    "rules_fpgrowth_kategori.csv")

cat("\n[SELESAI] Semua output telah dibuat.\n")
cat("  Visualisasi : viz_01 s/d viz_05 (.png)\n")
cat("  Rules CSV   : rules_apriori_kategori.csv, rules_fpgrowth_kategori.csv\n\n")
