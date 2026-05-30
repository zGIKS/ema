{ pkgs ? import <nixpkgs> { }, withML ? false }:

pkgs.mkShell {
  packages = [
    pkgs.uv
    # Needed by manylinux wheels (e.g. numpy) when installed via uv/pip.
    pkgs.stdenv.cc.cc.lib
    pkgs.zlib
    (pkgs.python313.withPackages (ps:
      let
        core = (with ps; [
          fastapi
          uvicorn
          pydantic
          pydantic-settings
          python-multipart
          numpy
          httpx
        ]);
        ml = (with ps; [
          insightface
          onnxruntime
          opencv-python-headless
        ]);
      in
      core ++ pkgs.lib.optionals withML ml))
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  '';
}
