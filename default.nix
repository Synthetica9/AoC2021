let
  pkgs = import (builtins.fetchTarball
    "https://github.com/nixos/nixpkgs/archive/nixpkgs-unstable.tar.gz") { };

  inherit (pkgs) lib jq runCommand python310 gnumake;

  src = ./.;
  days = lib.importJSON
    (pkgs.runCommand "out.json" { buildInputs = [ pkgs.jq ]; } ''
      cd ${src}
      ls | grep day | jq -R | jq -s > $out
    '');

  mkDay = day:
    pkgs.runCommand "${day}.log" {
      buildInputs = [ gnumake python310 ];
      src = ./${day};
    } ''
      cd $src
      make | tee $out
    '';
in lib.listToAttrs (map (day: {
  name = day;
  value = mkDay day;
}) days)
