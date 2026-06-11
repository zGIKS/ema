{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  packages = [
    pkgs.uv
    pkgs.curl
    # Needed by manylinux wheels (e.g. numpy) when installed via uv/pip.
    pkgs.stdenv.cc.cc.lib
    pkgs.zlib
    (pkgs.python313.withPackages (ps: with ps; [
      fastapi
      uvicorn
      pydantic
      pydantic-settings
      python-dotenv
      python-multipart
      pyjwt
      sqlalchemy
      asyncpg
      numpy
      httpx
      insightface
      onnxruntime
      opencv-python-headless
    ]))
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

    cat <<'EOF'
Face Recognition API

.env is loaded automatically.

Run:
  uvicorn src.main:app --host 0.0.0.0 --port 8080

Optional:
  curl http://127.0.0.1:8080/docs
EOF
  '';
}
