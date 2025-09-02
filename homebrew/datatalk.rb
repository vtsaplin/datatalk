class Datatalk < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/vtsaplin/datatalk"
  url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.3.tar.gz"
  sha256 "3772aa66b2d505a7960c9d1c6e32068582298e527c4d6775c5559cff48958de3"
  license "MIT"
  head "https://github.com/vtsaplin/datatalk.git", branch: "main"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/datatalk", "--help"
  end
end
