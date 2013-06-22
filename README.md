hfhom
=====

A package to compute Heergaard Floer correction terms for some classes of manifolds, as a SURF 2013 project.

alink
-----
Used to compute the terms for a double branched cover of an alternating link, with input supplied in a .lnk file.
A .lnk file can be acquired using the SnapPea application, by issuing the command 'Manifold()' to the SnapPea command line.
This opens a link editor, and use PLink->Make Alternating to ensure an alternating link. File->Save As will create a .lnk
file at a location of your choosing. To compute the terms at the level of the operating system's shell, on a UNIX system 
run 
    $ ./alink YOUR_LINK_FILE.lnk
which will return a plaintext list of correction terms. 
To redirect the list into a file called `out.txt`, issue 
    $ ./alink YOUR_LINK.lnk > out.txt
To use the correction terms inside a Python program, 
    import hfhom.alink
    ...
    with open('YOUR_KNOT_FILE.lnk') as links:
        corr_terms = hfhom.alink.ct_from_link(links) 
    ...

Plans are made to extend the package to more classes of Manifolds at present.
