package com.web;

import com.alipay.api.AlipayApiException;
import com.alipay.api.AlipayClient;
import com.alipay.api.request.AlipayTradePagePayRequest;
import com.zhifubao.AppUtil;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@Controller
public class PayController {
    @Resource
    private AlipayClient alipayClient;
    @Resource
    private AlipayTradePagePayRequest alipayTradePagePayRequest;


    //处理支付请求
    //1.接收页面传过来的数据:订单号，金额，名称，商品描述  表单中的name值=参数名
    @RequestMapping("/pay")
    public void pay(String WIDout_trade_no, String WIDsubject, String WIDtotal_amount, String WIDbody, HttpServletResponse response)
         throws AlipayApiException, IOException {
        //2.获得支付的客户端AlipayClient,和配置支付信息的对象AlipayTradePagePayRequest
        //3.设置响应的地址(支付宝返回给商户的响应地址)
        alipayTradePagePayRequest.setNotifyUrl(AppUtil.notify_url);
        alipayTradePagePayRequest.setReturnUrl(AppUtil.return_url);
        //4.设置请求的参数(传递给支付宝的数据)
        alipayTradePagePayRequest.setBizContent(
                "{\"out_trade_no\":\""+ WIDout_trade_no +"\","
                + "\"total_amount\":\""+ WIDtotal_amount +"\","
                + "\"subject\":\""+ WIDsubject +"\","
                + "\"body\":\""+ WIDbody +"\","
                + "\"product_code\":\"FAST_INSTANT_TRADE_PAY\"}");
        //5.发送请求
        String result = alipayClient.pageExecute(alipayTradePagePayRequest).getBody();
        //6.将响应结果返回给前端
        response.setContentType("text/html;charset=utf-8");
        response.getWriter().println(result);
    }
}
