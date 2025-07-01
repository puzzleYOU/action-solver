{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in with pkgs; {
        devShell = mkShell {
          buildInputs = [
            (pkgs.python312.withPackages (devDependencies: [
              devDependencies.pip
              devDependencies.setuptools
              devDependencies.black
              devDependencies.flake8
              devDependencies.isort
            ]))
          ];
        };
      }
    );
}
