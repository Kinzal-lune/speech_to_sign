using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

[Serializable]
public class SignPayload
{
    public string transcript;
    public string[] signs;
}

public class SignPayloadReceiver : MonoBehaviour
{
    [Header("HTTP Receiver")]
    public bool enableHttp = true;
    public int httpPort = 5000;

    [Header("Socket Receiver")]
    public bool enableSocket = true;
    public int socketPort = 8765;

    private HttpListener _httpListener;
    private TcpListener _tcpListener;
    private Thread _httpThread;
    private Thread _socketThread;

    private readonly Queue<string> _incoming = new Queue<string>();
    private readonly object _lock = new object();

    void Start()
    {
        if (enableHttp)
        {
            _httpThread = new Thread(HttpLoop) { IsBackground = true };
            _httpThread.Start();
        }

        if (enableSocket)
        {
            _socketThread = new Thread(SocketLoop) { IsBackground = true };
            _socketThread.Start();
        }
    }

    void Update()
    {
        lock (_lock)
        {
            while (_incoming.Count > 0)
            {
                string raw = _incoming.Dequeue();
                var payload = JsonUtility.FromJson<SignPayload>(raw);
                Debug.Log($"Transcript: {payload.transcript}");
                Debug.Log($"Signs: {string.Join(",", payload.signs)}");
                // TODO: map payload.signs[] to avatar animation triggers.
            }
        }
    }

    void HttpLoop()
    {
        _httpListener = new HttpListener();
        _httpListener.Prefixes.Add($"http://*:{httpPort}/sign-sequence/");
        _httpListener.Start();

        while (_httpListener.IsListening)
        {
            try
            {
                var ctx = _httpListener.GetContext();
                using var reader = new StreamReader(ctx.Request.InputStream, ctx.Request.ContentEncoding);
                string body = reader.ReadToEnd();
                Enqueue(body);

                byte[] responseBytes = Encoding.UTF8.GetBytes("ok");
                ctx.Response.StatusCode = 200;
                ctx.Response.OutputStream.Write(responseBytes, 0, responseBytes.Length);
                ctx.Response.Close();
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"HTTP receiver error: {ex.Message}");
            }
        }
    }

    void SocketLoop()
    {
        _tcpListener = new TcpListener(IPAddress.Any, socketPort);
        _tcpListener.Start();

        while (true)
        {
            try
            {
                using TcpClient client = _tcpListener.AcceptTcpClient();
                using NetworkStream stream = client.GetStream();
                using var reader = new StreamReader(stream, Encoding.UTF8);
                string body = reader.ReadLine();
                if (!string.IsNullOrEmpty(body))
                {
                    Enqueue(body);
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Socket receiver error: {ex.Message}");
            }
        }
    }

    void Enqueue(string payload)
    {
        lock (_lock)
        {
            _incoming.Enqueue(payload);
        }
    }

    void OnDestroy()
    {
        _httpListener?.Stop();
        _tcpListener?.Stop();
    }
}
