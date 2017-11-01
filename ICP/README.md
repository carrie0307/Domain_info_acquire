# ICP获取与比对

------

* 从[站长之家](http://icp.chinaz.com)获取icp信息：

    * python get_chinaz_icp.py（注意修改表名）

    * 这里存在被ban的情况，采用了之前写的ip_proxy工具。但是由于获取ip代理时也可能被ban，因此会有一些报错信息产生，但并未影响程序的正常获取

* 从网站页面上获取icp信息：

    * python get_page_icp.py（注意修改表名）

* 站长之家icp与页面icp的一致性比对

    * python cmp.py （注意修改表名）

    * 具体比对方式见代码中注释

* icp信息的查重

    * python duplicate_icp.py （注意修改表名）

    * 具体查重方式见代码中注释


* ICP统计结果和相关文档，见“统计结果.md”
