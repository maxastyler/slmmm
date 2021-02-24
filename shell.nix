{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = [
    pkgs.hello
    ((pkgs.python3.withPackages (ps:
      with ps; [
        numpy
        python-language-server
        pyls-mypy
        grpcio
        grpcio-tools
        pyqt5
      ])).override (args: { ignoreCollisions = true; }))
    pkgs.qt5Full
    # keep this line if you use bash
    pkgs.bashInteractive
    pkgs.nixfmt
  ];
}
