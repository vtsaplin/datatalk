class Datatalk < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/vtsaplin/datatalk"
  url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.4.tar.gz"
  sha256 "94f4219b522d221c919af36b3fb14731b99d4bdcc31aba59d24c022b4d9ca2af"
  license "MIT"
  head "https://github.com/vtsaplin/datatalk.git", branch: "main"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/datatalk", "--help"
  end
end
