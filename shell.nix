{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python313
    uv
    gcc.cc.lib
    zlib
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.gcc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH"
    echo "NixOS environment ready."
    echo "To install dependencies: uv pip install -r requirements.txt"
    echo "To run: uv run python main.py"
  '';
}
