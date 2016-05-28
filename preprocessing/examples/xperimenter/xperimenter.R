#!/usr/bin/env Rscript

################################################################################
### get command-line arguments
################################################################################
args <- commandArgs(TRUE)
paramspathname <- args[1]

################################################################################
### read parameters
################################################################################
read.params <- function(paramspathname) {
  data <- readLines(paramspathname)
  data <- strsplit(data, split = ",")
  param <- function(x) {setNames(list(x[-1]), x[1])}
  sapply(data, param)
}

################################################################################
### !!!!!!!!!!!! CUSTOMIZE THIS SECTION TO YOUR APPLICATION !!!!!!!!!!!!!!!!!!!!
################################################################################
cmd <- function() {"./preprocessing_script.py"}

enquote <- function(str) {paste("\"", paste(str, "\"", sep = ''), sep = "")}

arglist <- function(params) {
  # Create a string of param names
  return(paste(enquote(params$`Input Directory`),
               enquote(params$`Output Directory`),
               sep=" "))
}

################################################################################
### main
################################################################################
params <- read.params(paramspathname)

out <- paste(params$`Output Directory`, "out", sep = "/")
err <- paste(params$`Output Directory`, "err", sep = "/")

y <- system2(command = cmd(), args = arglist(params),
             stdout = out, stderr = err, wait = TRUE)

################################################################################
### exit
################################################################################
q(status = y)
