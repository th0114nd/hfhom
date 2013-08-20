hfhom
=====
<!---
Install pandoc (http://johnmacfarlane.net/pandoc/)
Convert to html by cd'ing into the directory with the README file, then using
$ pandoc -f markdown -t html README.md -o README.html
-->
A package to compute Heergaard Floer correction terms for some classes of manifolds, as a SURF 2013 project.

Installation
------------
You will need to first install `matplotlib`, with instructions available [here]
(matplotlib.org/users/installing.html).

Using the GUI
-----
The GUI has two tabs, one for computing the corrections terms of the double
branched cover of an alternating link, and one for computing the correction
terms of a plumbed 3-manifold. Input for the double branched cover of an
alternating link is an alternating link from either 
[Knotilus](http://knotilus.math.uwo.ca/) or 
[Plink](http://www.math.uic.edu/t3m/SnapPy/plink.html).
Input for a plumbed 3-manifold is either Seifert data for a Seifert fibered
rational homology sphere or a negative definite weighted graph with at most
two bad vertices.

![](images/gui.png)

From the inputted data, a negative definite quadratic form is computed,
and then the Heegaard Floer correction terms are computed from the quadratic
form.

### Knotilus archive ###
The [Knotilus archive](http://knotilus.math.uwo.ca/) section has two input
methods, either by entering an archive number or opening a saved file download
from the Knotilus database.

* __Entering an archive number__  
Archive numbers must be of the form ax-b-c, for integers a, b, and c. 
For example, 6x-1-1 or 20x-5-10. This method requires an Internet connection,
and may take up to 20 seconds to load the link for 11 or more crossings.
Visiting the link's database page with your browser and letting it load first
will significantly decrease the program's running time. If the checkbutton
`Save file` is selected, the plaintext data from the Knotilus database is
saved in the current directory as `ax-b-c.txt`. Press the `Go` button
when finished entering the archive number.
See [here](http://knotilus.math.uwo.ca/doc/archive.html) for more details
about the Knotilus archive number.

* __Loading a downloaded Knotilus file__  
A valid Knotilus file is created by going to [Knotilus](http://knotilus.math.uwo.ca/), finding the desired link, then selecting
`Download > Plaintext` and saving the file. 
The program will run noticeably faster on a downloaded Knotilus file
than if it must fetch the file from the database. The option `original link`
will only work if the filename is of the form `ax-b-c.txt` or `ax-b-c`.
It will be ignored otherwise.

### PLink/SnapPy ###
The PLink/SnapPy section has two input methods, either by drawing a new link
using the PLink Editor or opening a saved PLink file. Instruction for using
PLink can be found in the documentation for SnapPy, [here](http://www.math.uic.edu/t3m/SnapPy/plink.html).

* __Drawing a new link__  
Clicking the `Create New` button will open the PLink editor. Draw the link 
in the editor. Ensure the link is alternating, or use the menu option 
`Tools > Make alternating`.
When finished drawing the link, close the window. A dialog to save the file
will appear. If you choose not to save the file, the program will not be able 
to check that your link is closed and alternating, and the option 
`original link` will be ignored. If the link is not closed and alternating, 
results will be unpredictable.

* __Loading a saved PLink file__  
A valid PLink file is created by drawing a link in the PLink editor, then using
the menu option `File > Save ...`.
Clicking the `Open` button will load the open file dialog to select a valid 
PLink file.

### Seifert data ###
Data for a Seifert fibered rational homology sphere is represented as a list
`[e,(p1,q1),...,(pr,qr)]`, where e and all the pi, qi are integers, and all
pi > 1 with gcd(pi, qi) = 1.

### Weighted graph editor ###


### Options ###
Under the `Options` menu, there are two global options, `Show quadratic form`
and `Condense correction terms`. Additionally, there is the submenu
`Double branched cover`, which has the options `Show original link`,
`Show shaded link`, and `Show graph commands`. These last three options only
affect the input methods on the `Double branched cover` tab (Knotilus and 
PLink/SnapPy).

* __Global Options__  
If the `quadratic form` option is checked, the quadratic form
(square matrix) will be printed, in addition to the correction terms, in the
output window. Checking the `condense correction terms` box will disable the
`quadratic form` and `graph commands` options, and the output window will just
contain the Knotilus archive number or filename, followed by a space and the
correction terms, all on a single line.

* __Double branched cover submenu__  
If the `original link` option is checked, a separate window will open to show
the original link diagram. For Knotilus, this will open an Internet browser tab
to the appropriate link. If opening a saved Knotilus file, this will only
succeed if the filename is of the form `ax-b-c.txt` or `ax-b-c`, where 'ax-b-c'
is the archive number. For PLink or SnapPy, the PLink editor will open with the
original link drawing. The PLink file must be saved in order to do this.

