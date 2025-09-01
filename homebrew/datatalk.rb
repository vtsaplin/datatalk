class Datatalk < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/tsaplin/datatalk"
  url "https://github.com/tsaplin/datatalk/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "SHA256_HASH_HERE"
  license "MIT"
  head "https://github.com/tsaplin/datatalk.git", branch: "main"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/datatalk", "--help"
  end
end
