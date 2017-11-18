Packaging and Deploying get_sepsis_score_python

1. Prerequisites for Deployment 

A. If MATLAB Runtime version 9.2 (R2017a) has not been installed, install it in one of 
   these ways:

i. Run the package installer, which will also install the MATLAB Runtime.

ii. Download the Linux 64-bit version of the MATLAB Runtime for R2017a from:

    http://www.mathworks.com/products/compiler/mcr/index.html
   
iii. Run the MATLAB Runtime installer provided with MATLAB.

B. Verify that a Linux 64-bit version of Python 2.7, 3.4, and/or 3.5 is installed.

2. Installing the get_sepsis_score_python Package

A. Go to the directory that contains the file setup.py and the subdirectory 
   get_sepsis_score_python. If you do not have write permissions, copy all its contents 
   to a temporary location and go there.

B. Execute the command:

    python setup.py install [options]
    
If you have full administrator privileges, and install to the default location, you do 
   not need to specify any options. Otherwise, use --user to install to your home folder, 
   or --prefix="installdir" to install to "installdir". In the latter case, add 
   "installdir" to the PYTHONPATH environment variable. For details, refer to:

    https://docs.python.org/2/install/index.html

C. Copy the following to a text editor:

setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:<MCR_ROOT>/v90/runtime/glnxa64:<MCR_ROOT>/v90/bin/glnxa64:<MCR_ROOT>/v90/sys/os/glnxa64:<MCR_ROOT>/v90/sys/opengl/lib/glnxa64
setenv XAPPLRESDIR <MCR_ROOT>/v90/X11/app-defaults

Make the following changes:
- If LD_LIBRARY_PATH is not yet defined, remove the string "${LD_LIBRARY_PATH}:". 
- Replace "<MCR_ROOT>" with the directory where the MATLAB Runtime is installed.
- If your shell does not support setenv, use a different command to set the environment 
   variables.

Finally, execute the commands or add them to your shell initialization file.

3. Using the get_sepsis_score_python Package

The get_sepsis_score_python package is on your Python path. To import it into a Python 
   script or session, execute:

    import get_sepsis_score_python

If a namespace must be specified for the package, modify the import statement accordingly.

———————————————————————————————
score = get_sepsis_score_python(var1, var2, var3, var4, var5, var6, var7, var8, var9, var10, var11, var12, var13, var14, var15, var16, var17, var18, var19, var20, var21, var22, var23, var24, var25, var26, var27, var28, var29, var30, var31, var32, var33, var34, var35)

35 inputs:
         HR,...  %1
	 SaO2, ... %2
	 Temp, ... %3
	 SBP, ... %4
	 MAP, ... %5
	 DBP, ... %6
	 Resp, ... %7
	 EtCO2, ... %8
	 BaseExcess, ... %9
	 HCO3, ... %10
	 FiO2, ... %11
	 pH, ... %12
	 PaCO2, ... %13
	 O2Sat, ... %14
	 AST, ...%15
	 BUN, ...%16
	 Alkalinephos, ...%17
	 Calcium, ...%18
	 Chloride, ...%19
	 Creatinine, ...%20
	 Bilirubin_direct, ...%21
	 Glucose, ...%22
	 Magnesium, ...%23
	 Phosphate, ...%24
	 Potassium, ...%25
	 Bilirubin_total, ...%26
	 TroponinI, ...%27
	 Hct, ...%28
	 Hgb, ...%29
	 PTT, ...%30
	 WBC, ...%31
	 Fibrinogen, ...%32
	 Platelets, ...%33

        Age ... %34
        Gender ... %35   if "Female", Gender=-1; elseif "Male", Gender=1; else, Gender=0

