using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Net;
using System.Threading;
using Cysharp.Threading.Tasks;

public class udpTesterScript : MonoBehaviour
{
    UdpClient udpClient;
    IPEndPoint receiveEP = new IPEndPoint(IPAddress.Parse("127.0.0.1"), 62000);
    IPEndPoint senderEP = null;
    bool isReceieving = false;
    Dictionary<string, string> sendDataDict = new Dictionary<string, string>();
    Dictionary<string, string> ReceievedDataDict = new Dictionary<string, string>();

    async void Awake()
    {
        
        
    }

    void Start()
    {
        udpClient = new UdpClient(receiveEP);
        var CancellationTokenOnDestroy = this.GetCancellationTokenOnDestroy();
        UniTask.Create(async () => { await UniTask.CompletedTask; WaitReceieve(CancellationTokenOnDestroy).Forget(); }).Forget();
        //UniTask.Run(async () => { await UniTask.CompletedTask; WaitReceieve(CancellationTokenOnDestroy).Forget(); });
        //WaitReceieve(CancellationTokenOnDestroy).Forget();
    }

    async UniTask<byte[]> udpClientReceive(CancellationToken cancellationToken)
    {
        await UniTask.CompletedTask;
        return udpClient.Receive(ref senderEP);
    }

    async UniTask WaitReceieve(CancellationToken cancellationToken)
    {
        await UniTask.SwitchToThreadPool();
        isReceieving = true;
        while (isReceieving)
        {
            Debug.Log("waiting receive");
            byte[] receivedBytes = await udpClientReceive(cancellationToken);
            var receivedDataJson = System.Text.Encoding.UTF8.GetString(receivedBytes);
            var receivedDataDict = JsonUtility.FromJson<Dictionary<string, string>>(receivedDataJson);
            Debug.Log(receivedDataDict);
        }
    }

    public void SendMessageUDP()
    {
        var dstEP = new IPEndPoint(IPAddress.Parse("127.0.0.1"), 62000);
        sendDataDict["0"] = "aaaa";
        //string sendDataJson = JsonSerializer.Serialize(sendDataDict);
        string sendDataJson = JsonUtility.ToJson(sendDataDict);
        byte[] sendDataByte = System.Text.Encoding.UTF8.GetBytes(sendDataJson);
        udpClient.SendAsync(sendDataByte, sendDataByte.Length, dstEP);
    }
}
