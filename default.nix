let
  pkgs = import (builtins.fetchTarball
    "https://github.com/nixos/nixpkgs/archive/nixpkgs-unstable.tar.gz") { };

  inherit (pkgs) lib jq runCommand python310 gnumake;

  myPython = python310.withPackages (p: with p; [more-itertools rich]);

  common = pkgs.runCommand "common" {} ''
    mkdir -p $out
    cp -r ${./common} $out/common
  '';

  src = ./.;
  days = lib.importJSON
    (pkgs.runCommand "out.json" { buildInputs = [ pkgs.jq ]; } ''
      cd ${src}
      ls | grep day | jq -R | jq -s > $out
    '');

  mkDay = day:
    pkgs.runCommand "${day}.log" {
      buildInputs = [ gnumake myPython ];
      src = ./${day};
    } ''
      export PYTHONPATH="${common}:$PYTHONPATH"
      echo $PYTHONPATH
      cd $src
      make | tee $out
    '';
in lib.listToAttrs (map (day: {
  name = day;
  value = mkDay day;
}) days)
