let pkgs = import <nixpkgs> { };
in with pkgs;

let
  ourPython = python3;
  pycplex = ourPython.pkgs.buildPythonPackage rec {
    pname = "cplex";
    version = fullcplex.version;

    src = "${fullcplex}/cplex/python/${
        lib.versions.majorMinor ourPython.version
      }/x86-64_linux/";

    unpackPhase = ''
      echo $src
      cp -r $src/* /build
    '';
  };

  rich = with ourPython.pkgs;
    buildPythonPackage rec {
      pname = "rich";
      version = "9.2.0";

      src = fetchPypi {
        inherit pname version;
        sha256 = "15gj95gksq38ag1a35k89a6j0zmnlh09n2969b9z96xpwg6a20vh";
      };

      propagatedBuildInputs =
        [ pygments typing-extensions CommonMark colorama ];

      doCheck = false;
    };

  py = ourPython.withPackages
    (p: with p; [ numpy pyqt5 docplex pycplex ruamel_yaml rich rx ]);

  fullcplex = cplex.override {
    # releasePath = ./cos_installer_preview-12.10.0.0.R2-Linux-CC43LML.bin;
    releasePath = ./cplex_studio1210.linux-x86-64.bin;
  };

in mkShell {
  buildInputs = [ fullcplex py ];

}
