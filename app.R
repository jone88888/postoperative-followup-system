library(shiny)
library(shinyWidgets)
library(DT)
library(dplyr)
library(magrittr)
library(Seurat)
library(infercnv)
library(rtracklayer)

# =========================
# 工具函数
# =========================

# 从Seurat对象读取metadata列名
get_metadata_cols <- function(seurat_obj) {
  colnames(seurat_obj@meta.data)
}

# 生成gene order文件
prepare_gene_order <- function(gtf_file, output_file) {
  genome_annotation <- rtracklayer::import(gtf_file)
  genome_annotation <- as.data.frame(genome_annotation) %>%
    dplyr::select(gene_name, seqnames, start, end) %>%
    dplyr::rename(Gene = gene_name, chr = seqnames)

  genome_annotation <- genome_annotation[!duplicated(genome_annotation$Gene), ]

  write.table(
    genome_annotation,
    file = output_file,
    sep = "\t",
    quote = FALSE,
    row.names = FALSE,
    col.names = FALSE
  )
  return(output_file)
}

# 生成annotation文件
prepare_annotation <- function(pbmc, group_col, tissue_col, normal_label, tumor_label = NULL, cell_filter_regex = NULL, output_file) {
  meta <- pbmc@meta.data
  if (!group_col %in% colnames(meta)) stop("分组列不存在")
  if (!tissue_col %in% colnames(meta)) stop("条件列不存在")

  # 组合分组名：例如 "12_Normal"
  meta$celltype.group <- paste0(meta[[group_col]], "_", meta[[tissue_col]])

  anno <- data.frame(
    cell = rownames(meta),
    group = meta$celltype.group,
    stringsAsFactors = FALSE
  )

  # 按regex过滤细胞
  if (!is.null(cell_filter_regex) && nchar(cell_filter_regex) > 0) {
    anno <- anno[grepl(cell_filter_regex, anno$group), , drop = FALSE]
  }

  # 如果用户指定了正常组标签，确保匹配
  # 例如 normal_label = "Normal" -> group里要存在 "12_Normal"
  # infercnv ref_group_names需要完整组名
  write.table(
    anno,
    file = output_file,
    sep = "\t",
    quote = FALSE,
    row.names = FALSE,
    col.names = FALSE
  )

  return(anno)
}

# 创建输出目录
make_run_dir <- function(base_dir = "output") {
  timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
  run_dir <- file.path(base_dir, paste0("infercnv_run_", timestamp))
  dir.create(run_dir, recursive = TRUE, showWarnings = FALSE)
  run_dir
}

# 压缩目录为zip
zip_dir <- function(zipfile, files) {
  old <- getwd()
  on.exit(setwd(old), add = TRUE)

  tmpdir <- tempdir()
  setwd(tmpdir)

  # files可以是单个目录
  utils::zip(zipfile = zipfile, files = files, flags = "-r9Xq")
  return(zipfile)
}

# =========================
# UI
# =========================
ui <- fluidPage(
  titlePanel("inferCNV 单细胞分析 Shiny 图形界面版"),

  sidebarLayout(
    sidebarPanel(
      fileInput(
        inputId = "seurat_rds",
        label = "1. 上传 Seurat 对象 (.rds)",
        accept = c(".rds")
      ),

      tags$hr(),

      uiOutput("meta_select_ui"),

      textInput(
        inputId = "cell_filter_regex",
        label = "2. 细胞筛选正则表达式（可选）",
        value = "^(12|0_)"
      ),

      textInput(
        inputId = "ref_group_names",
        label = "3. 参考组名称（多个用逗号分隔）",
        value = "0_Normal"
      ),

      tags$hr(),

      radioButtons(
        inputId = "gene_order_mode",
        label = "4. 基因顺序文件输入方式",
        choices = c("上传 gene order txt" = "txt", "上传 GTF 自动生成" = "gtf"),
        selected = "gtf"
      ),

      conditionalPanel(
        condition = "input.gene_order_mode == 'gtf'",
        fileInput(
          inputId = "gtf_file",
          label = "上传 GTF 文件",
          accept = c(".gtf", ".gtf.gz")
        )
      ),

      conditionalPanel(
        condition = "input.gene_order_mode == 'txt'",
        fileInput(
          inputId = "gene_order_file",
          label = "上传 gene order 文件",
          accept = c(".txt", ".tsv")
        )
      ),

      tags$hr(),

      numericInput(
        inputId = "cutoff",
        label = "5. cutoff",
        value = 0.1,
        min = 0,
        step = 0.05
      ),

      numericInput(
        inputId = "num_threads",
        label = "线程数",
        value = 4,
        min = 1,
        step = 1
      ),

      numericInput(
        inputId = "k_obs_groups",
        label = "k_obs_groups",
        value = 1,
        min = 1,
        step = 1
      ),

      checkboxInput(
        inputId = "cluster_by_groups",
        label = "cluster_by_groups",
        value = FALSE
      ),

      checkboxInput(
        inputId = "denoise",
        label = "denoise",
        value = TRUE
      ),

      checkboxInput(
        inputId = "HMM",
        label = "HMM",
        value = FALSE
      ),

      tags$hr(),

      actionButton(
        inputId = "run_btn",
        label = "开始运行 inferCNV",
        class = "btn-primary"
      ),

      tags$hr(),

      downloadButton("download_zip", "下载结果压缩包"),
      br(), br(),
      downloadButton("download_annotation", "下载注释文件"),
      br(), br(),
      downloadButton("download_gene_order", "下载 gene order 文件"),
      br(), br(),
      downloadButton("download_log", "下载运行日志")
    ),

    mainPanel(
      tabsetPanel(
        tabPanel(
          "运行状态",
          verbatimTextOutput("status_text")
        ),
        tabPanel(
          "Seurat元数据",
          DTOutput("meta_table")
        ),
        tabPanel(
          "日志",
          verbatimTextOutput("log_text")
        )
      )
    )
  )
)

# =========================
# Server
# =========================
server <- function(input, output, session) {

  rv <- reactiveValues(
    pbmc = NULL,
    meta_cols = NULL,
    annotation_file = NULL,
    gene_order_file = NULL,
    run_dir = NULL,
    log_file = NULL,
    status = "等待上传文件...",
    last_message = ""
  )

  append_log <- function(msg) {
    if (is.null(rv$log_file)) return()
    line <- paste0(format(Sys.time(), "%Y-%m-%d %H:%M:%S"), " | ", msg, "\n")
    cat(line, file = rv$log_file, append = TRUE)
    rv$last_message <- msg
    rv$status <- msg
  }

  # 上传Seurat对象后读取meta.data列
  observeEvent(input$seurat_rds, {
    req(input$seurat_rds)
    tryCatch({
      pbmc <- readRDS(input$seurat_rds$datapath)
      rv$pbmc <- pbmc
      rv$meta_cols <- colnames(pbmc@meta.data)
      rv$status <- "Seurat对象读取成功"
      rv$last_message <- "Seurat对象读取成功"
    }, error = function(e) {
      rv$status <- paste0("读取Seurat对象失败: ", e$message)
      rv$last_message <- rv$status
    })
  })

  # 动态生成metadata列选择
  output$meta_select_ui <- renderUI({
    req(rv$meta_cols)
    tagList(
      selectInput(
        inputId = "group_col",
        label = "分组列（例如 seurat_clusters）",
        choices = rv$meta_cols,
        selected = if ("seurat_clusters" %in% rv$meta_cols) "seurat_clusters" else rv$meta_cols[1]
      ),
      selectInput(
        inputId = "tissue_col",
        label = "条件列（例如 tissue_type）",
        choices = rv$meta_cols,
        selected = if ("tissue_type" %in% rv$meta_cols) "tissue_type" else rv$meta_cols[1]
      )
    )
  })

  # 展示元数据表
  output$meta_table <- renderDT({
    req(rv$pbmc)
    datatable(head(rv$pbmc@meta.data, 50), options = list(scrollX = TRUE, pageLength = 10))
  })

  # 点击运行
  observeEvent(input$run_btn, {
    req(rv$pbmc)

    isolate({
      rv$run_dir <- make_run_dir("output")
      dir.create(rv$run_dir, recursive = TRUE, showWarnings = FALSE)
      rv$log_file <- file.path(rv$run_dir, "run.log")
      writeLines(character(), rv$log_file)

      append_log("开始运行 inferCNV 流程...")

      withProgress(message = "inferCNV运行中", value = 0, {

        # 1. 处理gene order文件
        gene_order_out <- file.path(rv$run_dir, "gene_order.txt")

        incProgress(0.15, detail = "准备 gene order 文件")

        if (input$gene_order_mode == "gtf") {
          req(input$gtf_file)
          append_log("使用GTF自动生成gene order文件")
          tryCatch({
            prepare_gene_order(input$gtf_file$datapath, gene_order_out)
            rv$gene_order_file <- gene_order_out
            append_log(paste0("gene order文件已生成: ", gene_order_out))
          }, error = function(e) {
            append_log(paste0("gene order生成失败: ", e$message))
            stop(e)
          })
        } else {
          req(input$gene_order_file)
          append_log("使用上传的gene order文件")
          file.copy(input$gene_order_file$datapath, gene_order_out, overwrite = TRUE)
          rv$gene_order_file <- gene_order_out
        }

        incProgress(0.20, detail = "生成注释文件")

        # 2. 生成注释文件
        anno_out <- file.path(rv$run_dir, "infercnv_annotations.txt")
        tryCatch({
          anno <- prepare_annotation(
            pbmc = rv$pbmc,
            group_col = input$group_col,
            tissue_col = input$tissue_col,
            normal_label = NULL,
            cell_filter_regex = input$cell_filter_regex,
            output_file = anno_out
          )
          rv$annotation_file <- anno_out
          append_log(paste0("注释文件已生成: ", anno_out))
          append_log(paste0("保留细胞数: ", nrow(anno)))
        }, error = function(e) {
          append_log(paste0("生成注释文件失败: ", e$message))
          stop(e)
        })

        incProgress(0.20, detail = "整理表达矩阵")

        # 3. 获取counts矩阵并筛选细胞
        matrix_count <- GetAssayData(rv$pbmc, assay = "RNA", layer = "counts")

        anno <- read.table(rv$annotation_file, sep = "\t", header = FALSE, stringsAsFactors = FALSE)
        colnames(anno) <- c("cell", "group")

        # 保证矩阵细胞顺序和注释一致
        common_cells <- intersect(colnames(matrix_count), anno$cell)
        matrix_count <- matrix_count[, common_cells, drop = FALSE]
        anno <- anno[match(common_cells, anno$cell), , drop = FALSE]

        # 重新写一份对齐后的注释文件
        write.table(
          anno,
          file = rv$annotation_file,
          sep = "\t",
          quote = FALSE,
          row.names = FALSE,
          col.names = FALSE
        )

        append_log(paste0("表达矩阵细胞数: ", ncol(matrix_count)))

        incProgress(0.20, detail = "创建 inferCNV 对象")

        # 4. 创建infercnv对象
        ref_groups <- trimws(unlist(strsplit(input$ref_group_names, ",")))

        infercnv_obj <- CreateInfercnvObject(
          raw_counts_matrix = matrix_count,
          annotations_file = rv$annotation_file,
          gene_order_file = rv$gene_order_file,
          delim = "\t",
          ref_group_names = ref_groups
        )

        incProgress(0.25, detail = "运行 inferCNV")

        # 5. 运行inferCNV
        infercnv_obj <- infercnv::run(
          infercnv_obj,
          cutoff = input$cutoff,
          out_dir = file.path(rv$run_dir, "inf"),
          cluster_by_groups = input$cluster_by_groups,
          k_obs_groups = input$k_obs_groups,
          HMM = input$HMM,
          denoise = input$denoise,
          num_threads = input$num_threads,
          write_expr_matrix = TRUE
        )

        # 6. 保存对象
        save(infercnv_obj, file = file.path(rv$run_dir, "infercnv_obj.rdata"))

        append_log("inferCNV运行完成")
        rv$status <- paste0("运行完成，结果目录：", rv$run_dir)
        incProgress(1, detail = "完成")
      })
    })
  })

  output$status_text <- renderText({
    rv$status
  })

  output$log_text <- renderText({
    if (is.null(rv$log_file) || !file.exists(rv$log_file)) {
      return("暂无日志")
    }
    paste(readLines(rv$log_file, warn = FALSE), collapse = "\n")
  })

  # 下载结果压缩包
  output$download_zip <- downloadHandler(
    filename = function() {
      paste0("infercnv_result_", format(Sys.time(), "%Y%m%d_%H%M%S"), ".zip")
    },
    content = function(file) {
      req(rv$run_dir)
      oldwd <- getwd()
      on.exit(setwd(oldwd), add = TRUE)

      setwd(dirname(rv$run_dir))
      zip::zipr(
        zipfile = file,
        files = basename(rv$run_dir)
      )
    }
  )

  # 下载注释文件
  output$download_annotation <- downloadHandler(
    filename = function() {
      "infercnv_annotations.txt"
    },
    content = function(file) {
      req(rv$annotation_file)
      file.copy(rv$annotation_file, file, overwrite = TRUE)
    }
  )

  # 下载gene order文件
  output$download_gene_order <- downloadHandler(
    filename = function() {
      "gene_order.txt"
    },
    content = function(file) {
      req(rv$gene_order_file)
      file.copy(rv$gene_order_file, file, overwrite = TRUE)
    }
  )

  # 下载日志文件
  output$download_log <- downloadHandler(
    filename = function() {
      "run.log"
    },
    content = function(file) {
      req(rv$log_file)
      file.copy(rv$log_file, file, overwrite = TRUE)
    }
  )
}

shinyApp(ui, server)
