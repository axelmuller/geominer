# Setting up the cloud environment

```
sudo apt-get install htop
```
## install anaconda

```bash
wget 'https://repo.continuum.io/archive/Anaconda2-5.0.0.1-Linux-x86_64.sh' 
bash Anaconda3-5.0.0.1-Linux-x86_64.sh
```

Allow adding path to .bashrc 

```bash
source ~/.bashrc
```

## install R
```
sudo apt-get install r-base
```

## install python packages
```bash
conda install pandas numpy 
pip install flashtext pronto
```

**Make sure conda is activated**
in case of errors check python version
`python --version` 
if the result is not:
Python 3.6.2 :: Anaconda custom (64-bit)
run:

```bash
source ~/.bashrc
```


## install R packages
First some dependencies
```bash



The script install_R_packages.r contains the R code to install all required packages.
Open R in the terminal 
```bash
R
```
and enter the following code

```R
install.packages("devtools", dependencies = TRUE)
``` 
Select appropriate mirror

```R
source("https://bioconductor.org/biocLite.R")
biocLite("GEOmetadb")
```

	
