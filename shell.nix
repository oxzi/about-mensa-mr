with import <nixpkgs> {};

(pkgs.python3.withPackages (ps: with ps; [
  ipykernel jupyterlab
  matplotlib numpy pandas seaborn
])).env
