{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  packages = [
    (pkgs.python313.withPackages (ps: with ps; [
      fastapi
      uvicorn
      pydantic
      pydantic-settings
      python-multipart
      numpy
      httpx
    ]))
  ];
}
