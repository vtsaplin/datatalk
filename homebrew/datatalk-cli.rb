class DatatalkCli < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/vtsaplin/datatalk"
  url "https://files.pythonhosted.org/packages/source/d/datatalk-cli/datatalk_cli-0.1.0.tar.gz"
  sha256 "b8b1ec9d68e1cd08305021ba6097c01893cca33a6fe044e38a72e3b192d3553f"
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
